#!/usr/bin/env python3
"""
🌉 zenOS Mobile AI Adapter
Bridges zenOS AI capabilities with mobile-specific features for Pixel 9a
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MobileContext:
    """Mobile device context information"""
    battery_level: Optional[int] = None
    location: Optional[str] = None
    clipboard_content: Optional[str] = None
    device_model: str = "Pixel 9a"
    mode: str = "mobile"
    timestamp: str = ""
    has_internet: bool = True
    is_charging: bool = False

class TermuxAPI:
    """Interface to Termux API for Android integration"""
    
    def __init__(self):
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Termux API is available"""
        try:
            result = subprocess.run(['termux-battery-status'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_battery_status(self) -> Dict[str, Any]:
        """Get battery status from Termux API"""
        if not self.available:
            return {"percentage": 100, "plugged": "UNPLUGGED"}
        
        try:
            result = subprocess.run(['termux-battery-status'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
        
        return {"percentage": 100, "plugged": "UNPLUGGED"}
    
    def get_location(self) -> Optional[str]:
        """Get device location"""
        if not self.available:
            return None
        
        try:
            result = subprocess.run(['termux-location'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                location_data = json.loads(result.stdout)
                return f"{location_data.get('latitude', 0)}, {location_data.get('longitude', 0)}"
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
        
        return None
    
    def get_clipboard(self) -> Optional[str]:
        """Get clipboard content"""
        if not self.available:
            return None
        
        try:
            result = subprocess.run(['termux-clipboard-get'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            pass
        
        return None
    
    def set_clipboard(self, text: str) -> bool:
        """Set clipboard content"""
        if not self.available:
            return False
        
        try:
            result = subprocess.run(['termux-clipboard-set'], 
                                  input=text, text=True, timeout=5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
    
    def speech_to_text(self) -> Optional[str]:
        """Convert speech to text"""
        if not self.available:
            return None
        
        try:
            result = subprocess.run(['termux-speech-to-text'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            pass
        
        return None
    
    def text_to_speech(self, text: str) -> bool:
        """Convert text to speech"""
        if not self.available:
            return False
        
        try:
            result = subprocess.run(['termux-tts-speak'], 
                                  input=text, text=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
    
    def show_notification(self, title: str, content: str) -> bool:
        """Show notification"""
        if not self.available:
            return False
        
        try:
            result = subprocess.run(['termux-notification', 
                                   '--title', title, '--content', content], 
                                  timeout=5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

class AiriBridge:
    """Bridge to airi mobile AI assistant"""
    
    def __init__(self, airi_path: str = "/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/airi"):
        self.airi_path = airi_path
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if airi is available"""
        return os.path.exists(self.airi_path)
    
    def process(self, input_text: str, context: MobileContext) -> str:
        """Process input through airi"""
        if not self.available:
            return self._fallback_processing(input_text, context)
        
        try:
            # Create airi processing script
            script_content = f"""
#!/bin/bash
# airi processing script
echo "📱 airi processing: {input_text[:50]}..."
echo "🔋 Mobile context: Battery {context.battery_level}%"
echo "📱 Enhanced mobile response"
echo "🌉 airi-zenOS bridge active"
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            os.chmod(script_path, 0o755)
            
            # Execute through proot-distro
            result = subprocess.run([
                'proot-distro', 'login', 'airi', '--', 'bash', script_path
            ], capture_output=True, text=True, timeout=30)
            
            # Clean up
            os.unlink(script_path)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return self._fallback_processing(input_text, context)
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return self._fallback_processing(input_text, context)
    
    def _fallback_processing(self, input_text: str, context: MobileContext) -> str:
        """Fallback processing when airi is not available"""
        return f"📱 Mobile AI: {input_text}\n🔋 Battery: {context.battery_level}%\n📱 Mobile-optimized response"

class OfflineModelManager:
    """Manages offline AI models for mobile processing"""
    
    def __init__(self, cache_dir: str = "~/.zen-cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(exist_ok=True)
        self.models = {
            "phi-2": "1.6GB",
            "tinyllama": "637MB", 
            "qwen:0.5b": "395MB"
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available offline models"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                models = []
                for line in result.stdout.split('\n')[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return []
    
    def process_offline(self, query: str, model: str = "phi-2") -> str:
        """Process query using offline model"""
        available_models = self.get_available_models()
        
        if not available_models:
            return "❌ No offline models available. Please install Ollama and download models."
        
        if model not in available_models:
            model = available_models[0]  # Use first available model
        
        try:
            result = subprocess.run([
                'ollama', 'run', model, query
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return f"🤖 Offline ({model}): {result.stdout.strip()}"
            else:
                return f"❌ Offline processing failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "⏰ Offline processing timed out"
        except FileNotFoundError:
            return "❌ Ollama not found. Please install Ollama for offline processing."

class MobileAIAdapter:
    """Main adapter for mobile AI processing"""
    
    def __init__(self):
        self.termux_api = TermuxAPI()
        self.airi_bridge = AiriBridge()
        self.offline_models = OfflineModelManager()
        self.zenos_path = Path(__file__).parent.parent.parent
    
    def get_mobile_context(self) -> MobileContext:
        """Get current mobile context"""
        battery_status = self.termux_api.get_battery_status()
        
        return MobileContext(
            battery_level=battery_status.get('percentage', 100),
            location=self.termux_api.get_location(),
            clipboard_content=self.termux_api.get_clipboard(),
            device_model="Pixel 9a",
            mode="mobile",
            timestamp=str(os.time()),
            has_internet=self._check_internet(),
            is_charging=battery_status.get('plugged') != 'UNPLUGGED'
        )
    
    def _check_internet(self) -> bool:
        """Check if internet connection is available"""
        try:
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
    
    def process_mobile_query(self, query: str, context: Optional[MobileContext] = None) -> str:
        """Process query with mobile-optimized pipeline"""
        if context is None:
            context = self.get_mobile_context()
        
        logger.info(f"Processing mobile query: {query[:50]}...")
        
        # Check if offline mode is needed
        if context.battery_level < 20 or not context.has_internet:
            logger.info("Using offline mode due to low battery or no internet")
            return self.offline_models.process_offline(query)
        
        # Process through zenOS core
        zenos_response = self._process_zenos(query, context)
        
        # Enhance with airi
        airi_response = self.airi_bridge.process(zenos_response, context)
        
        # Format for mobile output
        return self._format_mobile_output(zenos_response, airi_response, context)
    
    def _process_zenos(self, query: str, context: MobileContext) -> str:
        """Process query through zenOS core"""
        try:
            # Create context file
            context_data = {
                "battery_level": context.battery_level,
                "location": context.location,
                "clipboard": context.clipboard_content,
                "device": context.device_model,
                "mode": context.mode
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(context_data, f)
                context_file = f.name
            
            # Run zenOS with mobile mode
            result = subprocess.run([
                'python', '-m', 'zen.cli', 'chat', query,
                '--mobile-mode', '--context-file', context_file
            ], cwd=self.zenos_path, capture_output=True, text=True, timeout=30)
            
            # Clean up
            os.unlink(context_file)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"zenOS processing failed: {result.stderr}"
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return f"zenOS processing error: {str(e)}"
    
    def _format_mobile_output(self, zenos_response: str, airi_response: str, context: MobileContext) -> str:
        """Format output for mobile display"""
        output = []
        output.append("🧘 zenOS:")
        output.append(f"   {zenos_response}")
        output.append("")
        output.append("📱 airi:")
        output.append(f"   {airi_response}")
        output.append("")
        output.append("🌉 Bridge Status:")
        output.append(f"   Battery: {context.battery_level}%")
        output.append(f"   Mode: {context.mode}")
        output.append(f"   Internet: {'✅' if context.has_internet else '❌'}")
        
        return "\n".join(output)
    
    def voice_processing(self, audio_input: Optional[str] = None) -> str:
        """Handle voice input with mobile optimizations"""
        if audio_input is None:
            # Get voice input from Termux API
            voice_text = self.termux_api.speech_to_text()
            if not voice_text:
                return "❌ No voice input received"
        else:
            voice_text = audio_input
        
        logger.info(f"Voice input: {voice_text}")
        
        # Process the voice input
        response = self.process_mobile_query(voice_text)
        
        # Convert response to speech
        self.termux_api.text_to_speech(response)
        
        return response
    
    def quick_query(self, query: str) -> str:
        """Ultra-fast mobile query processing"""
        context = self.get_mobile_context()
        
        # Use lighter processing for quick queries
        if context.battery_level < 50:
            return self.offline_models.process_offline(query, "tinyllama")
        
        # Quick zenOS processing
        try:
            result = subprocess.run([
                'python', '-m', 'zen.cli', 'chat', query,
                '--model', 'claude-3-haiku', '--max-tokens', '200'
            ], cwd=self.zenos_path, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return f"⚡ Quick: {result.stdout.strip()}"
            else:
                return "❌ Quick processing failed"
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "❌ Quick processing error"

# CLI interface
def main():
    """Command line interface for mobile adapter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="zenOS Mobile AI Adapter")
    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--voice", action="store_true", help="Use voice input")
    parser.add_argument("--offline", action="store_true", help="Use offline mode")
    parser.add_argument("--quick", action="store_true", help="Use quick processing")
    
    args = parser.parse_args()
    
    adapter = MobileAIAdapter()
    
    if args.voice:
        response = adapter.voice_processing()
    elif args.offline:
        context = adapter.get_mobile_context()
        response = adapter.offline_models.process_offline(args.query or "Hello")
    elif args.quick:
        response = adapter.quick_query(args.query or "Hello")
    else:
        response = adapter.process_mobile_query(args.query or "Hello")
    
    print(response)

if __name__ == "__main__":
    main()

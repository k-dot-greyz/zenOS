#!/usr/bin/env python3
"""
zenOS Setup System Test Suite

This script demonstrates and tests the unified setup system across different scenarios.
It shows how the setup system handles various environments and edge cases.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class SetupTester:
    def __init__(self):
        self.test_results = []
        self.temp_dirs = []
    
    def create_test_environment(self, name: str, scenario: str) -> Path:
        """Create a test environment for a specific scenario"""
        temp_dir = tempfile.mkdtemp(prefix=f"zenos_test_{name}_")
        self.temp_dirs.append(temp_dir)
        
        # Copy zenOS to temp directory
        zenos_source = Path.cwd()
        test_zenos = Path(temp_dir) / "zenOS"
        shutil.copytree(zenos_source, test_zenos, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '*.pyc', '.pytest_cache', 'test_*'
        ))
        
        # Set up scenario-specific conditions
        if scenario == "clean":
            # Clean environment - no git, no configs
            pass
        elif scenario == "dirty":
            # Dirty environment - has unwanted files
            (test_zenos / "__pycache__").mkdir()
            (test_zenos / ".DS_Store").write_text("dirty file")
            (test_zenos / "node_modules").mkdir()
        elif scenario == "partial":
            # Partial setup - has git but no MCP
            subprocess.run(["git", "init"], cwd=test_zenos, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=test_zenos, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=test_zenos, check=True)
        
        return test_zenos
    
    def run_setup_test(self, name: str, scenario: str, options: list = None) -> dict:
        """Run setup test for a specific scenario"""
        console.print(f"\n🧪 Testing: {name} ({scenario})")
        
        # Create test environment
        test_dir = self.create_test_environment(name, scenario)
        
        # Run setup
        cmd = [sys.executable, "setup.py"] + (options or [])
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=test_dir, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            test_result = {
                "name": name,
                "scenario": scenario,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
            if test_result["success"]:
                console.print(f"✅ {name} passed")
            else:
                console.print(f"❌ {name} failed (exit code: {result.returncode})")
                if result.stderr:
                    console.print(f"Error: {result.stderr[:200]}...")
            
            self.test_results.append(test_result)
            return test_result
            
        except subprocess.TimeoutExpired:
            console.print(f"⏰ {name} timed out")
            return {
                "name": name,
                "scenario": scenario,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            console.print(f"💥 {name} crashed: {e}")
            return {
                "name": name,
                "scenario": scenario,
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self):
        """Clean up test environments"""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                console.print(f"Warning: Could not clean up {temp_dir}: {e}")
    
    def print_summary(self):
        """Print test results summary"""
        console.print("\n" + "="*60)
        console.print(Panel.fit("🧪 Setup System Test Results", style="bold cyan"))
        
        table = Table(title="Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Scenario", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Notes", style="white")
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            if result["success"]:
                passed += 1
            else:
                failed += 1
            
            notes = ""
            if not result["success"]:
                if "error" in result:
                    notes = result["error"]
                elif result.get("returncode"):
                    notes = f"Exit code: {result['returncode']}"
            
            table.add_row(
                result["name"],
                result["scenario"],
                status,
                notes
            )
        
        console.print(table)
        console.print(f"\n📊 Summary: {passed} passed, {failed} failed")
        
        if failed == 0:
            console.print(Panel.fit("🎉 All tests passed! Setup system is working perfectly!", style="bold green"))
        else:
            console.print(Panel.fit(f"⚠️  {failed} test(s) failed. Check the details above.", style="bold yellow"))

@click.command()
@click.option('--scenario', type=click.Choice(['all', 'clean', 'dirty', 'partial', 'phases']), 
              default='all', help='Which test scenario to run')
@click.option('--unattended', is_flag=True, help='Run in unattended mode')
def main(scenario, unattended):
    """Test the zenOS unified setup system"""
    
    console.print(Panel.fit(
        "🧪 zenOS Setup System Test Suite\n"
        "Testing the unified setup system across different scenarios",
        style="bold blue"
    ))
    
    tester = SetupTester()
    options = ["--unattended"] if unattended else []
    
    try:
        if scenario in ['all', 'clean']:
            # Test 1: Clean environment
            tester.run_setup_test("Clean Environment", "clean", options)
        
        if scenario in ['all', 'dirty']:
            # Test 2: Dirty environment with unwanted files
            tester.run_setup_test("Dirty Environment", "dirty", options)
        
        if scenario in ['all', 'partial']:
            # Test 3: Partial setup (has git, no MCP)
            tester.run_setup_test("Partial Setup", "partial", options)
        
        if scenario in ['all', 'phases']:
            # Test 4: Phase-by-phase execution
            console.print("\n🔧 Testing phase-by-phase execution...")
            
            phases = ['detection', 'validation', 'git_setup', 'mcp_setup', 'zenos_setup', 'verification']
            for phase in phases:
                tester.run_setup_test(f"Phase: {phase}", "clean", options + [f"--phase={phase}"])
        
        # Test 5: Validation only
        tester.run_setup_test("Validation Only", "clean", options + ["--validate-only"])
        
    finally:
        tester.print_summary()
        tester.cleanup()

if __name__ == "__main__":
    main()

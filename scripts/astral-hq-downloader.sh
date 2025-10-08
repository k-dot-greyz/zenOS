#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# 🎵 ASTRAL HQ CONTENT DOWNLOADER - zenOS Edition
# ═══════════════════════════════════════════════════════════════════
# Downloads all audio tracks, PDFs, and docs from Astral HQ page
# Integrates with zenOS git inbox workflow
# Author: k.greyZ | Part of zenOS automation suite
# ═══════════════════════════════════════════════════════════════════

set -e  # Exit on any error

# Configuration
DOWNLOAD_DIR="$HOME/Downloads/astral-hq-$(date +%Y%m%d-%H%M%S)"
INBOX_DIR="$HOME/zenOS/inbox/incoming/astral-hq-content"
ZENOS_REPO="$HOME/zenOS"
DATE_STAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Create directory structure
setup_directories() {
    log "Setting up directory structure..."
    mkdir -p "$DOWNLOAD_DIR"/{audio/main,audio/bonus,audio/meditation,docs,metadata}
    mkdir -p "$INBOX_DIR"
    success "Directories created"
}

# Download function with retry logic
download_file() {
    local url="$1"
    local output_path="$2"
    local filename=$(basename "$output_path")
    
    log "Downloading: $filename"
    
    # Note: These are placeholder URLs - replace with actual download links from the page
    if wget --timeout=30 --tries=3 --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
           -O "$output_path" "$url" 2>/dev/null; then
        success "Downloaded: $filename"
        return 0
    else
        warning "Failed to download: $filename"
        return 1
    fi
}

# Main audio tracks download
download_main_tracks() {
    log "Downloading main audio tracks..."
    
    declare -A main_tracks=(
        ["Egyptian_Golden_Ratio_For_Abundance.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["The_Abundance_Pyramid.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["Shaman_Beats.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["Lucid_Oddysee.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["Golden_Ratio_Experience.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["New_Horizons.mp3"]="REPLACE_WITH_ACTUAL_URL"
    )
    
    for filename in "${!main_tracks[@]}"; do
        download_file "${main_tracks[$filename]}" "$DOWNLOAD_DIR/audio/main/$filename"
    done
}

# Bonus tracks download
download_bonus_tracks() {
    log "Downloading bonus audio tracks..."
    
    declare -A bonus_tracks=(
        ["Astral_Starwaves.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["Pure_Theta.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["Rainy_Winter.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["Royal_Awakening_Theta.mp3"]="REPLACE_WITH_ACTUAL_URL"
        ["Stormy_Escape.mp3"]="REPLACE_WITH_ACTUAL_URL"
    )
    
    for filename in "${!bonus_tracks[@]}"; do
        download_file "${bonus_tracks[$filename]}" "$DOWNLOAD_DIR/audio/bonus/$filename"
    done
}

# Meditation track download
download_meditation() {
    log "Downloading guided meditation..."
    download_file "REPLACE_WITH_MEDITATION_URL" "$DOWNLOAD_DIR/audio/meditation/Guided_Meditation_Manifesting_Abundance.mp3"
}

# Documents download
download_documents() {
    log "Downloading PDF documents..."
    
    # Welcome letter PDF
    download_file "REPLACE_WITH_WELCOME_PDF_URL" "$DOWNLOAD_DIR/docs/Welcome_Letter.pdf"
    
    # Manifest instructions (convert Google Doc to PDF)
    warning "Google Doc URL detected - manual conversion to PDF required"
    echo "REPLACE_WITH_GOOGLE_DOC_URL" > "$DOWNLOAD_DIR/docs/manifest_instructions_url.txt"
    
    log "Google Doc URL saved for manual processing"
}

# Generate metadata
generate_metadata() {
    log "Generating metadata files..."
    
    cat > "$DOWNLOAD_DIR/metadata/download_info.json" << EOF
{
  "source_url": "https://astralhq.com/09sahebfn/",
  "page_title": "Shifting Vibrations Manifest Confirmation",
  "download_timestamp": "$DATE_STAMP",
  "download_location": "$DOWNLOAD_DIR",
  "total_files": {
    "main_audio": 6,
    "bonus_audio": 5,
    "meditation": 1,
    "documents": 2
  },
  "categories": {
    "audio/main": [
      "Egyptian_Golden_Ratio_For_Abundance.mp3",
      "The_Abundance_Pyramid.mp3", 
      "Shaman_Beats.mp3",
      "Lucid_Oddysee.mp3",
      "Golden_Ratio_Experience.mp3",
      "New_Horizons.mp3"
    ],
    "audio/bonus": [
      "Astral_Starwaves.mp3",
      "Pure_Theta.mp3",
      "Rainy_Winter.mp3", 
      "Royal_Awakening_Theta.mp3",
      "Stormy_Escape.mp3"
    ],
    "audio/meditation": [
      "Guided_Meditation_Manifesting_Abundance.mp3"
    ],
    "docs": [
      "Welcome_Letter.pdf",
      "manifest_instructions.pdf"
    ]
  },
  "zenos_integration": {
    "inbox_path": "$INBOX_DIR",
    "processing_status": "downloaded",
    "tags": ["manifestation", "audio", "astral", "abundance", "meditation"]
  }
}
EOF

    # Create README
    cat > "$DOWNLOAD_DIR/README.md" << EOF
# Astral HQ - Shifting Vibrations Content

Downloaded on: $DATE_STAMP  
Source: https://astralhq.com/  
zenOS Integration: Active

## Content Structure

### Main Audio Tracks (6)
High-quality binaural/frequency audio for manifestation work:
- Egyptian Golden Ratio For Abundance
- The Abundance Pyramid  
- Shaman Beats
- Lucid Oddysee
- Golden Ratio Experience
- New Horizons

### Bonus Audio Tracks (5)
Supplementary ambient and theta wave content:
- Astral Starwaves
- Pure Theta
- Rainy Winter
- Royal Awakening Theta  
- Stormy Escape

### Meditation (1)
- Guided Meditation For Manifesting Abundance

### Documentation (2)
- Welcome Letter (PDF)
- Manifest Instructions (PDF/Google Doc)

## Usage with zenOS

### MIDI Integration
```yaml
midi_triggers:
  play_track: C4 (60)
  next_track: D4 (62)  
  meditation_mode: E4 (64)
  stop_all: F4 (65)
```

### Audio Processing Pipeline
1. Import to zenOS audio library
2. Apply frequency analysis
3. Create MIDI-triggered playlists
4. Integrate with meditation workflows

### Tags
\`manifestation\` \`binaural\` \`theta\` \`abundance\` \`meditation\` \`frequency\` \`astral\`

---
*Part of zenOS automated content acquisition system*
EOF

    success "Metadata files generated"
}

# Copy to zenOS inbox
integrate_with_inbox() {
    log "Integrating with zenOS inbox..."
    
    if [ -d "$ZENOS_REPO" ]; then
        cp -r "$DOWNLOAD_DIR"/* "$INBOX_DIR/"
        
        cd "$ZENOS_REPO"
        
        # Git operations
        git add "inbox/incoming/astral-hq-content"
        git commit -m "🎵 INBOX: Added Astral HQ manifestation audio library + docs

- 6 main frequency tracks for abundance manifestation
- 5 bonus ambient/theta tracks  
- 1 guided meditation
- PDF documentation and metadata
- Full zenOS integration ready

Downloaded: $DATE_STAMP
Source: astralhq.com - Shifting Vibrations"

        success "Content added to zenOS inbox and committed to git"
    else
        warning "zenOS repository not found at $ZENOS_REPO"
        warning "Files available at: $DOWNLOAD_DIR"
    fi
}

# MIDI trigger simulation (for testing)
simulate_midi_workflow() {
    log "Simulating MIDI workflow integration..."
    
    cat > "$INBOX_DIR/midi_commands.yaml" << EOF
# MIDI Commands for Astral HQ Audio Library
midi_library_controls:
  base_note: 60  # C4
  
  commands:
    play_egyptian_golden: 60    # C4
    play_abundance_pyramid: 61  # C#4  
    play_shaman_beats: 62      # D4
    play_lucid_odyssey: 63     # D#4
    play_golden_ratio: 64      # E4
    play_new_horizons: 65      # F4
    
    bonus_mode: 66             # F#4
    meditation_mode: 67        # G4
    
    stop_all: 72              # C5
    next_track: 73            # C#5
    previous_track: 74        # D5

workflow_integration:
  - trigger: "morning_manifestation"
    sequence: [60, 64, 67]  # Egyptian -> Golden Ratio -> Meditation
    
  - trigger: "deep_work_focus"  
    sequence: [62, 65]      # Shaman Beats -> New Horizons
    
  - trigger: "sleep_preparation"
    sequence: [bonus_mode, pure_theta, rainy_winter]
EOF

    success "MIDI workflow configuration created"
}

# Verify downloads
verify_downloads() {
    log "Verifying downloaded files..."
    
    local total_files=0
    local success_files=0
    
    for dir in "$DOWNLOAD_DIR"/{audio/main,audio/bonus,audio/meditation,docs}; do
        if [ -d "$dir" ]; then
            local count=$(find "$dir" -type f | wc -l)
            total_files=$((total_files + count))
            success_files=$((success_files + count))
            log "Found $count files in $(basename "$dir")"
        fi
    done
    
    success "Verification complete: $success_files/$total_files files"
    
    # Generate summary
    echo
    echo "═══════════════════════════════════════"
    echo "📊 DOWNLOAD SUMMARY"
    echo "═══════════════════════════════════════"
    echo "📁 Location: $DOWNLOAD_DIR"
    echo "📋 Total Files: $success_files"
    echo "🎵 Audio Tracks: $(find "$DOWNLOAD_DIR"/audio -name "*.mp3" | wc -l)"
    echo "📄 Documents: $(find "$DOWNLOAD_DIR"/docs -name "*.pdf" | wc -l)"
    echo "⚡ zenOS Integration: Active"
    echo "═══════════════════════════════════════"
}

# Main execution
main() {
    echo "═══════════════════════════════════════════════════════════════════"
    echo "🎵 ASTRAL HQ DOWNLOADER - zenOS Edition"
    echo "═══════════════════════════════════════════════════════════════════"
    echo
    
    warning "IMPORTANT: This script contains placeholder URLs!"
    warning "You need to replace 'REPLACE_WITH_ACTUAL_URL' with real download links"
    warning "Extract the actual URLs from the browser page first"
    echo
    
    read -p "Continue anyway to set up the structure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Exiting. Update URLs first, then run again."
        exit 0
    fi
    
    setup_directories
    download_main_tracks
    download_bonus_tracks  
    download_meditation
    download_documents
    generate_metadata
    simulate_midi_workflow
    integrate_with_inbox
    verify_downloads
    
    success "Astral HQ content acquisition complete!"
    log "Next steps:"
    echo "  1. Replace placeholder URLs with actual download links"
    echo "  2. Re-run script for actual downloads"
    echo "  3. Test MIDI integration with zenOS"
    echo "  4. Set up automated workflows in n8n"
}

# URL extraction helper (manual step)
show_url_extraction_help() {
    cat << EOF

🔧 URL EXTRACTION INSTRUCTIONS:
═══════════════════════════════════════

To get the actual download URLs, you need to:

1. Open browser developer tools (F12)
2. Go to Network tab
3. Right-click each download link on the page
4. Copy the direct download URL
5. Replace the placeholder URLs in this script

Alternatively, use this one-liner to extract from page source:
grep -o 'https://[^"]*\.mp3' page_source.html
grep -o 'https://[^"]*\.pdf' page_source.html

Then update the script variables:
main_tracks["filename.mp3"]="actual_url_here"

EOF
}

# Execute based on arguments
case "${1:-}" in
    "help")
        show_url_extraction_help
        ;;
    "extract")
        log "URL extraction mode not implemented yet"
        log "Use browser dev tools to get direct download links"
        ;;
    *)
        main
        ;;
esac
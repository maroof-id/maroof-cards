#!/bin/bash
# Maroof - Complete Installation Script
# Digital Business Cards System

set -e  # Stop on any error

echo "=================================================="
echo "🎴 Maroof - Digital Business Cards System"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
REPO_PATH="/home/Xmoha4/maroof-id.github.io"
TOOLS_PATH="$REPO_PATH/tools"

# Check Python
echo -e "${BLUE}📋 Checking requirements...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not installed!"
    exit 1
fi
echo -e "${GREEN}✅ Python3 found${NC}"

# Check Git
if ! command -v git &> /dev/null; then
    echo "❌ Git not installed!"
    echo "📥 Installing..."
    sudo apt update
    sudo apt install -y git
fi
echo -e "${GREEN}✅ Git found${NC}"

# Check Repository
if [ ! -d "$REPO_PATH" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Repository not found!${NC}"
    echo "📥 Cloning from GitHub..."
    
    cd /home/Xmoha4
    git clone https://github.com/maroof-id/maroof-id.github.io.git
    
    echo -e "${GREEN}✅ Cloned successfully${NC}"
else
    echo -e "${GREEN}✅ Repository exists${NC}"
fi

# Navigate to project
cd "$REPO_PATH"

# Create directories
echo ""
echo -e "${BLUE}📁 Creating directories...${NC}"

mkdir -p templates
mkdir -p clients
mkdir -p tools
mkdir -p assets/{css,js,images}

echo -e "${GREEN}✅ Directories created${NC}"

# Copy files from /home/claude
echo ""
echo -e "${BLUE}📋 Copying project files...${NC}"

# Copy templates
if [ -f /home/claude/modern-template.html ]; then
    cp /home/claude/modern-template.html templates/modern.html
    echo "  ✓ modern.html"
fi

if [ -f /home/claude/classic-template.html ]; then
    cp /home/claude/classic-template.html templates/classic.html
    echo "  ✓ classic.html"
fi

if [ -f /home/claude/minimal-template.html ]; then
    cp /home/claude/minimal-template.html templates/minimal.html
    echo "  ✓ minimal.html"
fi

# Copy scripts
if [ -f /home/claude/create_card.py ]; then
    cp /home/claude/create_card.py tools/
    chmod +x tools/create_card.py
    echo "  ✓ create_card.py"
fi

if [ -f /home/claude/web_app.py ]; then
    cp /home/claude/web_app.py tools/
    chmod +x tools/web_app.py
    echo "  ✓ web_app.py"
fi

if [ -f /home/claude/nfc_writer.py ]; then
    cp /home/claude/nfc_writer.py tools/
    chmod +x tools/nfc_writer.py
    echo "  ✓ nfc_writer.py"
fi

echo -e "${GREEN}✅ Files copied${NC}"

# Install Python packages
echo ""
echo -e "${BLUE}📦 Installing Python packages...${NC}"

# Create requirements.txt
cat > tools/requirements.txt << 'EOF'
Flask==3.0.0
nfcpy==1.0.4
gitpython==3.1.40
qrcode==7.4.2
pillow==10.1.0
ndef==0.3.1
EOF

echo "  ⏳ Installing..."
pip3 install --break-system-packages -r tools/requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Packages installed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some issues during installation${NC}"
    echo "💡 You can install manually: pip3 install -r tools/requirements.txt --break-system-packages"
fi

# Create .gitignore
echo ""
echo -e "${BLUE}📝 Creating .gitignore...${NC}"

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Environment
.env

# IDE
.vscode/
.idea/

# System
.DS_Store
Thumbs.db

# Logs
*.log
EOF

echo -e "${GREEN}✅ .gitignore created${NC}"

# Setup Git
echo ""
echo -e "${BLUE}⚙️  Setting up Git...${NC}"

git config user.name "Maroof System" 2>/dev/null || true
git config user.email "maroof@example.com" 2>/dev/null || true

echo -e "${GREEN}✅ Git configured${NC}"

# Create quick start scripts
echo ""
echo -e "${BLUE}🚀 Creating startup scripts...${NC}"

# Web startup script
cat > start_web.sh << 'EOF'
#!/bin/bash
cd /home/Xmoha4/maroof-id.github.io
python3 tools/web_app.py
EOF
chmod +x start_web.sh

# Card creation script
cat > create.sh << 'EOF'
#!/bin/bash
cd /home/Xmoha4/maroof-id.github.io
python3 tools/create_card.py "$@"
EOF
chmod +x create.sh

echo -e "${GREEN}✅ Scripts created${NC}"

# Show summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Installation completed successfully!${NC}"
echo "=================================================="
echo ""
echo "📋 Installed files:"
echo "  ✓ 3 HTML templates (modern, classic, minimal)"
echo "  ✓ create_card.py (Card generator)"
echo "  ✓ web_app.py (Web interface)"
echo "  ✓ nfc_writer.py (NFC writer)"
echo ""
echo "🚀 Usage methods:"
echo ""
echo "  1️⃣  Web interface (from mobile):"
echo "      ./start_web.sh"
echo "      Then open: http://192.168.1.108:5000"
echo ""
echo "  2️⃣  Command line:"
echo "      ./create.sh --name \"Mohammed\" --phone 0501234567"
echo ""
echo "  3️⃣  NFC writing:"
echo "      python3 tools/nfc_writer.py --url \"LINK\""
echo ""
echo "=================================================="
echo ""
echo -e "${YELLOW}💡 Tip: Start with the web interface${NC}"
echo -e "${YELLOW}   Then open it from your phone!${NC}"
echo ""

# Ask to start web
read -p "Do you want to start the web interface now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting web interface..."
    ./start_web.sh
fi
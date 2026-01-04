# Maroof - Digital Business Cards with NFC

Professional digital business card system with NFC support, powered by Raspberry Pi.

## Features

- ✅ Web-based card creation interface
- ✅ NFC card writing/reading (PN532)
- ✅ Auto-push to GitHub Pages
- ✅ WhatsApp direct link integration
- ✅ vCard generation for contact saving
- ✅ Duplicate mode for mass production
- ✅ Sequential numbering for duplicate names
- ✅ Responsive design (mobile-friendly)
- ✅ Bilingual support (Arabic/English)

## Requirements

### Hardware
- Raspberry Pi (tested on Pi 5)
- PN532 NFC Reader/Writer
- NFC cards (NTAG215 recommended)

### Software
- Python 3.9+
- Flask
- nfcpy
- ndef

## Installation

### 1. Clone Repository

```bash
cd /home/Xmoha4/maroof
git clone https://github.com/maroof-id/maroof-cards.git
cd maroof-cards
```

### 2. Install Dependencies

```bash
pip3 install --break-system-packages -r tools/requirements.txt
```

### 3. Configure Git

```bash
git config user.name "Maroof System"
git config user.email "maroof@example.com"
```

### 4. Setup GitHub Token

```bash
# Create personal access token on GitHub
# Then configure:
git config credential.helper store
echo "https://USERNAME:TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
```

## Usage

### Start Web Server

```bash
python3 tools/web_app.py
```

Access: `http://raspberrypi.local:5000`

### Create Card via Command Line

```bash
python3 tools/create_card.py \
  --name "Mohammed" \
  --phone "0501234567" \
  --email "example@email.com" \
  --instagram "username" \
  --template modern
```

### NFC Operations

**Write URL to card:**
```bash
python3 tools/nfc_writer.py --write "https://maroof-id.github.io/maroof-cards/username"
```

**Read card:**
```bash
python3 tools/nfc_writer.py --read
```

## Web Interface

### Home Page (`/`)
- Create new card form
- Auto-push to GitHub on creation
- NFC write button
- QR code generation

### Settings Page (`/settings`)
- **Read Card**: Read existing NFC card
- **Duplicate Mode**: Copy existing card for mass production
- **Manual Write**: Write custom URL to NFC
- **Edit/Delete**: Modify or remove cards

## Workflow

### Scenario 1: New Card
```
1. Open http://raspberrypi.local:5000
2. Fill form (name, phone, email, social media)
3. Click "Create Card"
   → Saves to clients/username/
   → Auto-pushes to GitHub
   → Shows URL + QR code
4. Click "Write to NFC"
   → Place card on reader
   → Writes URL
   → Auto-pushes again
```

### Scenario 2: Duplicate Cards
```
1. Go to Settings
2. Click "Duplicate Card"
3. Place existing card
   → Reads data
   → Pre-fills form
4. Click "Create Card"
5. Click "Write to NFC" × N times
   → Write same data to multiple cards
```

### Scenario 3: Manual Write
```
1. Go to Settings
2. Click "Manual Write"
3. Enter custom URL
4. Click "Write to NFC"
   → No GitHub push
```

## File Structure

```
maroof-cards/
├── tools/
│   ├── create_card.py      # Card generator
│   ├── nfc_writer.py       # NFC handler
│   ├── web_app.py          # Web interface
│   └── requirements.txt    # Dependencies
├── templates/
│   ├── modern.html         # Modern template
│   ├── classic.html        # Classic template
│   └── minimal.html        # Minimal template
├── clients/
│   └── username/
│       ├── index.html      # Card page
│       ├── data.json       # Card data
│       ├── contact.vcf     # vCard file
│       └── photo.jpg       # (optional)
└── README.md
```

## Name Conflict Resolution

When creating cards with duplicate names, the system automatically adds sequential numbers:

```
mohammed → mohammed
mohammed → mohammed-1
mohammed → mohammed-2
...
```

## Auto-Push Events

Git push is triggered on:
1. Creating new card
2. Writing to NFC
3. Editing existing card

Commit messages:
- `"Add card: NAME"`
- `"Write to NFC: URL"`
- `"Update card: NAME"`

## Card URL Structure

```
https://maroof-id.github.io/maroof-cards/username
```

Features:
- Responsive design
- WhatsApp direct button
- Add to contacts (vCard)
- Social media links
- Hidden empty fields

## Troubleshooting

### NFC Reader Not Found
```bash
# Check USB connection
lsusb | grep PN532

# Test reader
python3 -c "import nfc; print(nfc.ContactlessFrontend('usb'))"
```

### Git Push Failed
```bash
# Check credentials
git config --list | grep credential

# Re-configure
bash tools/setup_github.sh
```

### Port 5000 Already in Use
```bash
# Kill existing process
sudo lsof -t -i:5000 | xargs kill -9

# Or use different port
python3 tools/web_app.py --port 5001
```

## API Endpoints

### POST `/api/create`
Create new card

**Request:**
```json
{
  "name": "Mohammed",
  "phone": "0501234567",
  "email": "example@email.com",
  "instagram": "username",
  "linkedin": "username",
  "twitter": "username",
  "bio": "Professional description",
  "template": "modern"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://maroof-id.github.io/maroof-cards/mohammed",
  "username": "mohammed"
}
```

### POST `/api/nfc/write`
Write URL to NFC card

**Request:**
```json
{
  "url": "https://maroof-id.github.io/maroof-cards/mohammed"
}
```

### GET `/api/nfc/read`
Read NFC card

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://maroof-id.github.io/maroof-cards/mohammed"
  }
}
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

## License

MIT

## Author

Maroof System - 2026
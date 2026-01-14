# 📦 Move Roadie to Your "elm" Project

## Quick Steps

1. Create a `roadie` folder in your elm project
2. Copy all Roadie files into it
3. Update paths if needed

## Terminal Commands

If your elm project is at a specific path, I can help you run these commands.

**Option 1: If you're in the Roadie directory:**
```bash
# Create roadie subfolder in elm project
mkdir -p /path/to/elm/roadie

# Copy everything (excluding .git if it exists)
rsync -av --exclude='.git' . /path/to/elm/roadie/
```

**Option 2: If you're in the elm project directory:**
```bash
# Copy Roadie folder into elm project
cp -r /path/to/roadie ./roadie
```

**Option 3: Manual (easiest):**
1. Create `roadie` folder in your elm project
2. Copy all files from this Roadie project into it
3. Done!

## After Moving

The structure will be:
```
elm/
├── (your existing files)
└── roadie/
    ├── backend/
    ├── frontend/
    ├── mobile/
    └── (all other files)
```

## Netlify Deployment

When deploying to Netlify from the elm repo:
- **Base directory**: `roadie/frontend`
- **Build command**: `cd roadie/frontend && npm run build`
- **Publish directory**: `roadie/frontend/.next`

Or update `netlify.toml` to reflect the new path.


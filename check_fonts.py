import os

def check_fonts():
    """Check if Urdu font files exist in assets/fonts/ folder."""
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts')
    
    # Define required font files
    jameel_font = "Jameel Noori Nastaleeq Regular.ttf"
    kasheeda_font = "Jameel Noori Nastaleeq Kasheeda.ttf"
    
    jameel_path = os.path.join(fonts_dir, jameel_font)
    kasheeda_path = os.path.join(fonts_dir, kasheeda_font)
    
    print("Font Verification Report")
    print("=" * 40)
    print(f"Fonts directory: {fonts_dir}")
    print()
    
    # Check Jameel Noori Nastaleeq Regular
    if os.path.exists(jameel_path):
        print(f"✅ Found: {jameel_font}")
    else:
        print(f"❌ Missing: {jameel_font}")
    
    # Check Jameel Noori Nastaleeq Kasheeda
    if os.path.exists(kasheeda_path):
        print(f"✅ Found: {kasheeda_font}")
    else:
        print(f"❌ Missing: {kasheeda_font}")
    
    print()
    
    # Provide download instructions if Jameel font is missing
    if not os.path.exists(jameel_path):
        print("Download Instructions:")
        print(f"Download Jameel Noori Nastaleeq from: https://www.urdufonts.net/fonts/jameel-noori-nastaleeq")
        print(f"Place the downloaded {jameel_font} file in: {fonts_dir}")
        print()
    
    # Summary
    found_count = sum([os.path.exists(jameel_path), os.path.exists(kasheeda_path)])
    total_count = 2
    
    print(f"Summary: {found_count}/{total_count} fonts found")
    
    if found_count == 0:
        print("⚠️  WARNING: No Urdu fonts found. Urdu text may not display correctly.")
    elif found_count == 1:
        print("ℹ️  One font found. Urdu text should display correctly.")
    else:
        print("✅ All fonts found. Urdu text will display correctly.")

if __name__ == "__main__":
    check_fonts()

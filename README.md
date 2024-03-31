# Sync-timing-subtitles 

<br>--> Transfer timing from other subtitles to ocr sub
  
## Usages
- Change parameters `characters`,`Dictionaries` in config.ini
- Can make your own SymSpell dictionary
- Run it

## Main Feature
- Sync sub based audio using sushi (if it from different version eg. BD and TVs)
- Auto-detect subtitles need combining or splitting
- Find and print caution unexpected characters (eg. japanese in ocr sub)
- Remove ocr lines got > 60% characters not in `characters` config.ini
- Spell checker using SymSpell
- Add ename dictionary to check names, locations
- Add filter rules to fix common error ( can use many methods ):
  + Replace
  + Regular expression
  + Replace word

## Setup / Build
- Install Python
- run cmd `pip install -r requirements.txt`
- Build using pyinstaller

Have fun

😸

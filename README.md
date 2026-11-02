# LT25 send presets to Fender Mustang LT25

Send some presets from the Google SpreadSheet to the Fender AMP via usb, due the manual config
is very painful. I have to add `self.amp.save_preset_as(json.dumps(data), True, slot_id)` function
to the library, so presets could be stored on amp.

## Install the library

Currently I'm working on a local copy of `ltamp` to add the fixes, but I need some requirements.
Install / Uninstall the official library does the trick to install the dependencies. GSpread is
used to download the available profiles in the famous google spreadsheet. For avoiding Google
auth, I use openpyxl with the exported sheet.

```sh
% python3.10 -m pip install ltamp
% python3.10 -m pip uninstall ltamp
% python3.10 -m pip install gspread
% python3.10 -m pip install openpyxl
```

```
## Resources

* [The SpreadSheet](https://docs.google.com/spreadsheets/d/1KWvjJ6q6Ora2MqmxtUAWjq9Uerp0Ycza5ouuKuol5HQ/edit?gid=1040178095#gid=1040178095)
* [The Library](https://github.com/benderhq/LtAmp.py)
* [The Web App](https://github.com/branimir-kirilov/ltamp-js/blob/main/src/amp.ts)

```js
savePresetAs: [55, { presetData: [1, "string"], isLoadPreset: [2, "bool"], presetSlot: [3, "int32"] }],

  async savePreset(slot: number, presetJson: string, { load = false } = {}): Promise<void> {
    assertSlot(slot);
    await this.request("savePresetAs", { presetData: presetJson, isLoadPreset: load, presetSlot: slot }, [
      "newPresetSavedStatus",
      "presetSavedStatus",
    ]);
  }
```

### How things are chained

```
PREFX  stompbox -> modulation ->
       amp -> 
POSTFX delay -> reverb

  blues - phaser - AMP (super clean) - reverse - arena
```

## data values (as measured in the application)

``````
on excel values: 6.0	7.5	4.0	3.0	7.0

gain 10 
volume 5
trebble 1
middle 10
bass 7

        FenderID:       DUBS_Twin57
        Node Parameters
        volume                   -13.988876   volume 5
        volume                   -60          volume 1.1
        volume                    0           volume 9.9
        volume                   -14          volume 5
        gatePreset               off
        gateDetectorPosition     jack
        cabsimType               65twn
        gain                     1            gain 10
        treb                     0            trebble 1
        mid                      1            middle 10
        bass                     0.666667     bass 7
        sag                      match
        bias                     0.5
        presence                 0.5
```

* Volume maps 1.0 (1.1) to 10 (9.9) in the range -60 .. 0
* All the parameters, maps 0 to 10 in the range 0.0 1.0


```
50S TWIN      Based on a 1957 Twin—an original-era 2x12” Fender tweed classic prized for clean-to-dirty versatility
60S UK CLN    Inspired by the Vox AC30, which powered the British Invasion and produced remarkable clean and dirty tone
70S ROCK      Inspired by a late-’60s/early-’70s Marshall Super Lead, the amp that powered the dawn of hard rock
70S UK CLN    Inspired by the original 100-watt Hiwatt DR103, which is the classic cleaner-tone British stack
80S ROCK      Inspired by the Marshall JCM800, which produced quintessential ’80s metal tone 
90S ROCK      Based on the Mesa Dual Rectifer, which featured distinctive distortion that shaped the “nu-metal” sound
BASSMAN       Based on the venerable ’59 Bassman® —one of Fender’s greatest tweed amps, which began life as a bass amp    
              before being adopted by countless guitarists
BURN          Based on the “burn” channel of the modern Fender Super-Sonic amp, which has two
              cascading preamp gain stages for pronounced sustain
CHAMP         Based on the ’57 Champ® —the small but mighty late-’50s Fender recording great
DELUXE CLN    Based on the highly popular 1965 Fender Deluxe Reverb® —an amp with great tone whether clean or dirty, and 
              cranked in countless clubs
DELUXE DIRT   Based on a 1957 Deluxe™—a medium-power late-’50s Fender tweed classic known for thick, compressed overdrive
DOOM METAL    Inspired by the “sludgy” majesty of the Orange OR120
EXCELSIOR     An elegantly eccentric modern-day Fender model with the distinctive thump of a 15” speaker
ALT METAL     Based on the distinctive nu-metal-defining distortion of the Mesa Dual Rectifier, gated with a very fast 
              attenuation curve especially ideal for high-gain metal
METAL 2000    Modern high-gain scorch based on the EVH® 5150III
PRINCETON     Based on a 1965 Princeton® —a mid-’60s Fender studio favorite with the snappy tone of a single 10” speaker
SMALLTONE     Inspired by the garage-classic 1960s Sears Silvertone beloved of retro/alternative players
SUPER CLEAN   Direct-to-mixing-desk studio-preamp purity with clean, uncolored tonal response
SUPER HEAVY   Modern high-gain scorch based on the EVH® 5150III, gated with a very fast attenuation curve especially 
              ideal for high-gain metal
TWIN CLEAN    Based on the 1965 Fender Twin Reverb® —an indispensable mid-’60s stage-andstudio favorite prized 
              for producing the Fender clean tone
```

on file amp_dump.txt is all the default parameters for each amp.
```
50S TWIN     DUBS_Twin57      65twn
60S UK CLN   DUBS_Ac30Tb      2x12c
70S ROCK     DUBS_Plexi87     4x12g2
70S UK CLN   DUBS_DR103       4x12v
80S ROCK     DUBS_Jcm800      4x12m
90S ROCK     DUBS_Rect2       4x12v2
BASSMAN      DUBS_Bassman59   59bman
BURN         DUBS_SuperSonic  1x12ss
CHAMP        DUBS_Twin57      65twn
DELUXE CLN   DUBS_Deluxe65    65dlx
DELUXE DIRT  DUBS_Twin57      65twn
DOOM METAL   DUBS_Or120       4x12m2
EXCELSIOR    DUBS_Excelsior   exlsr
ALT METAL    DUBS_MetalRect2  4x12r
METAL 2000   DUBS_Evh3        4x12g2
PRINCETON    DUBS_Princeton65 65prince
SMALLTONE    DUBS_Silvertone  57dlx
SUPER CLEAN  DUBS_Twin65      65twn
SUPER HEAVY  DUBS_MetalEvh3   4x12frd
TWIN CLEAN   DUBS_Twin65      65twn
```

## effects

### STOMP

```
OVERDRIVE         DUBS_Overdrive
BLUES DRIVE       DUBS_Greenbox
MYTH DRIVE        DUBS_MythicDrive
ROCK DIRT         DUBS_Blackbox
FUZZ              DUBS_VariFuzz
BIG FUZZ          DUBS_BigFuzz
OCTOBOT           DUBS_Octobot
COMPRESSOR        DUBS_SimpleCompressor
SUSTAIN           DUBS_Sustain
METAL GATE        DUBS_ChromeGate
5 BAND EQ         DUBS_MustangFiveBandEq1
```

### MODULATION

```
CHORUS          DUBS_ChorusTriangle
FLANGER         DUBS_TriangleFlanger
VIBRATONE       DUBS_Vibratone
TREMOLO         DUBS_SineTremolo
PHASER          DUBS_Phaser
STEP FILTER     DUBS_StepFilter
TOUCH WAH       DUBS_EcFilter
```

### DELAY

```
DELAY           DUBS_MonoDelay
REVERSE         DUBS_ReverseDelay
ECHO            DUBS_TapeDelayLite
```

### REVERB

```
LARGE HALL      DUBS_LargeHallReverb
SMALL ROOM      DUBS_SmallRoomReverb
SPRING 65       DUBS_Spring65
PLATE           DUBS_LargePlate
ARENA           DUBS_ArenaReverb
``````
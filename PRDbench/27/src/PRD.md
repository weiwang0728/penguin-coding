### Comprehensive Fortune Calculation System PRD

#### 1. Overview of Requirements
This project aims to develop a command-line comprehensive fortune calculation system based on traditional metaphysics and modern interactive patterns. Users will enter their basic personal information (name, date of birth, gender), participate in a "Fortune Drawing" interactive game to obtain their daily fortune sign, and submit their daily outfit color and jewelry type. The system will utilize the Five Element theory, Zodiac constellation theory, Munsell color system, and classical probability algorithms to generate a daily fortune report. The report will cover career suitability (whether you should go to work), lucky outfit suggestions (clothing color, jewelry type), and interpersonal interaction advice (best zodiac companion). The system must support persistent data storage of user information, ensuring that the calculation logic is traceable and results are consistent.

#### 2. Basic Function Requirements

##### 2.1 Personal Information Management Module
- On first use, guide the user to input their name (2–6 Chinese characters, with validity check), date of birth (Gregorian/Lunar selectable, with support for Lunar to Gregorian conversion and Heavenly Stems and Earthly Branches deduction), and gender (male/female/other, affects some metaphysics parameters).
- Support for local storage of user information (in JSON format); user information can be loaded or updated for subsequent use without repeated input.
- Date of birth input must be validated (e.g., no leap month dates, no future dates); abnormal input should provide Chinese error messages (e.g., "Month 13 is invalid, please re-enter").

##### 2.2 Fortune Drawing Interactive Game Module
- Implement two game modes: "Coin Slot Machine" (simulates slot machine, 3×3 grid with "Lucky", "Unlucky", "Neutral" symbols; probabilities for stopping outcomes are calculated using classical probability algorithms) and "Number Draw" (random number generator from 1–100, corresponding to different fortune sign levels; a normal distribution must be used so mid-level fortunes are more likely).
- At game start, display instructions (key operations, outcome rules); user selects game mode by number keys, and incorrect input prompts re-selection.
- After each game session, display the daily fortune sign result (six levels: Best, Very Lucky, Lucky, Neutral, Unlucky, Worst). The result is used as the basic weighting parameter for fortune calculation (weight range 1.2–0.6).

##### 2.3 Daily Status Input Module
- Guide the user to enter the main color of the day's outfit (supports "red/orange/yellow/green/blue/purple/black/white/grey", matching the hue dimension in the Munsell color system; if non-standard color entered, prompt available options).
- Allow input of jewelry type (metal/gemstone/crystal/no jewelry, each corresponds to a Five Element attribute: metal=metal, gemstone=earth, crystal=water). Incorrect input displays category explanation (e.g., "Metals include gold, silver, alloy accessories").
- All input data is temporarily stored; before generating the report, users may select "Re-enter" to modify the outfit or jewelry info.

##### 2.4 Comprehensive Fortune Calculation Module
- Use date of birth to deduce the user's Eight Characters (Ba Zi) and Five Elements (implement mapping between Heavenly Stems/Earthly Branches and the Five Elements, e.g., Jia Wood, Yi Wood = wood; Zi Water, Hai Water = water), and calculate the strength distribution of the Five Elements (prosperity index for metal/wood/water/fire/earth, range 0–10).
- Combine fortune sign weight, outfit color emotion value (based on color psychology—for example, red = excitement +0.3, blue = calm +0.2), and jewelry's Five Element attribute. Use a weighted formula to calculate the career luck index (range 0-100; <50 = not suitable for work, ≥50 = suitable for work).
- Based on the theory of zodiac constellation division, determine the sun sign according to the user's date of birth, and calculate the interaction index with the other 11 zodiac signs by combining the day's astrological configuration (using a fixed zodiac compatibility coefficient table, with the data file being `src/data/zodiac_compatibilities.json`), taking the highest value as the "best zodiac companion".

##### 2.5 Fortune Report Generation Module
- The report has a fixed structure: career suitability (clear "suitable for work" or "recommended to rest," with career index and influencing factors explanation), lucky outfit plan (recommended clothing color based on Five Element generating principle, e.g., if user's 'fire' element is strong, recommend 'water'-type blue shades; recommended jewelry based on Five Element supplementation, e.g., lacking metal, prioritize metal jewelry), and interpersonal advice (display best zodiac companion and interaction advantage, e.g., "Today, cooperating with Taurus brings partnership opportunities").
- Support formatted text output (with separators, bolded titles); key data (such as index values, constellation names) must be highlighted (in CLI, can be wrapped in special characters).
- After generating the report, ask if the user wants to save the result (as a txt file, filename includes the date).
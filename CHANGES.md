# Onsen Resort Management Game - Changes

## Dynamic ASCII Art for Onsen Pools
- Added dynamic ASCII art that displays all onsen pools with their actual sizes
- Implemented color-coding based on pool ingredients (e.g., green for Green Tea, yellow for Sulfur)
- Added a legend explaining the color-ingredient mapping
- Pools are displayed in rows of up to 3 pools each

## Daily Summary Improvements
- Added a facilities summary section showing counts of each facility type
- Added an accommodation summary showing room counts by type and total capacity
- All summaries are now displayed every day on the main screen

## Reputation System Changes
- Increased the reputation threshold for having no customers from 10 to 30
- Made reputation harder to maintain by changing the calculation from (avg_satisfaction - 50) / 10 to (avg_satisfaction - 50) / 8
- Added a daily reputation decay of 0.5 points for resorts with reputation above 50

## Event Visibility Improvements
- Added a dedicated "TODAY'S EVENTS" section to the day end summary
- Events now display with bullet points for better readability
- Shows "No special events occurred today" when there are no events

## ASCII Art Improvements
- Enhanced the main game title ASCII art with better borders and spacing
- Created a more detailed onsen pool ASCII art with multiple hot spring symbols
- Designed a more elaborate facility ASCII art with interior details

## Difficulty Increases
- Reduced starting capital from 100,000 to 75,000 yen
- Increased base daily operating costs from 5,000 to 8,000 yen
- Increased daily land rent from 10,000 to 15,000 yen
- Made pools get dirty faster (cleanliness decreases by 10-20 points per day instead of 5-15)
- Made all customer types more demanding:
  - Relaxation Seeker: Cleanliness 85→90, Staff Skill 60→70
  - Luxury Enthusiast: Cleanliness 95→98, Staff Skill 90→95
  - Health Conscious: Cleanliness 90→95, Staff Skill 70→75
  - Budget Traveler: Cleanliness 75→80, Staff Skill 50→55
  - Traditional Purist: Cleanliness 85→90, Staff Skill 80→85
  - Social Butterfly: Cleanliness 80→85

These changes make the game more challenging while improving the visual presentation and event visibility.

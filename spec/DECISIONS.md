# Architectural Decisions - Pitbit Soft Cooling

## Decision 1: Use of `undetected_chromedriver`
- **Context**: The Pitbit website may have anti-bot protections that block standard Selenium.
- **Decision**: Use the `undetected_chromedriver` library.
- **Rationale**: It bypasses most common bot detection mechanisms, allowing the script to interact with the web interface reliably.
- **Trade-offs**: Requires a local Chrome installation and a specific user data profile (`C:\selenium_profile`).

## Decision 2: Polling-based Monitoring
- **Context**: There is no public API for real-time temperature data from Pitbit.
- **Decision**: Periodically refresh/navigate to the miner status page to scrape temperature data.
- **Rationale**: Simple to implement and doesn't require complex reverse-engineering of private APIs.
- **Trade-offs**: Higher resource usage than an API-based approach; susceptible to UI changes.

## Decision 3: Gradual Adjustment (±1%)
- **Context**: Large, sudden changes in fan speed can be stressful for the hardware and may lead to "hunting" (oscillating around a target).
- **Decision**: Adjust fan speed in increments of 1% per check cycle.
- **Rationale**: Provides smooth control and allows the cooling system to react naturally to the changes.

## Decision 4: Confirmation Delay for Fan Decrease
- **Context**: Temperature can fluctuate briefly. Immediate fan speed reduction might lead to rapid cycling if the temperature bounces back up.
- **Decision**: Only decrease fan speed if the temperature has been below the threshold for `FAN_DECREASE_CONFIRM_TIME` (default 60s).
- **Rationale**: Ensures that cooling is only reduced when the miner is genuinely over-cooled, improving stability.

## Decision 5: CLI-First Configuration
- **Context**: Different miners and environments require different settings.
- **Decision**: Pass all major parameters via `sys.argv`.
- **Rationale**: Easy to automate via shell scripts or cron jobs without modifying the source code.

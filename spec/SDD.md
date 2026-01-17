# Software Design Document - Pitbit Soft Cooling

## Goal
The goal of this project is to provide automated, dynamic cooling management for crypto miners on the [pitbit.online](https://pitbit.online) platform. 

This tool was developed after realizing that Pitbit's built-in "smart management" often fails to maintain stable temperatures for certain miners—specifically those with manufacturing defects like poorly applied thermal paste. After a month of unsuccessful attempts to resolve these issues with Pitbit support, this custom controller was created. It has since demonstrated excellent results in stabilizing temperatures where the native system failed.

## Future Work
- **Broad Applicability Research**: Investigate if this granular control logic (±1% polling) can benefit other miner models by:
    - Reducing temperature spikes on chips.
    - Increasing the operational lifespan of the cooling fans.
    - Speeding up the transition to the most efficient operating mode.

## Scope (MVP)
The current implementation is a CLI tool that:
- Automates login to the Pitbit platform using a provided authentication key.
- Monitors a specific miner's temperature at regular intervals.
- Dynamically increases fan speed when the temperature exceeds a high threshold.
- Dynamically decreases fan speed when the temperature stays below a low threshold for a confirmed period.
- Uses an automated browser (`undetected_chromedriver`) to interact with the web interface.

### Hardware Compatibility
- **Tested on**: Antminer S21
- **Target Temperature**: Configured based on [Bitmain recommendations](https://support.bitmain.com/hc/en-us/articles/360005088914-Miner-Normal-Operating-Temperature-Range).

## User Scenarios
1. **Automated Maintenance**: A user starts the script with their miner ID and auth key. The script runs indefinitely, ensuring the miner stays within the 67-72°C range without manual intervention.
2. **Safety Override**: If the temperature spikes (e.g., due to ambient heat), the script quickly increases fan speed to prevent hardware damage.
3. **Noise/Power Reduction**: When the environment cools down, the script gradually lowers fan speeds to save power and reduce noise, provided the temperature remains low for a sufficient time.

## Functional Requirements
- **Monitoring**: Must fetch temperature from the miner's status page every `CHECK_INTERVAL` seconds.
- **Authentication**: Must handle session expiration by re-navigating to the fast-auth URL.
- **Cooling Logic**:
    - Increase fan speed by 1% if Temp >= `TEMP_MAX_OK + 1`.
    - Decrease fan speed by 1% if Temp <= `TEMP_MIN_OK - 1` for `FAN_DECREASE_CONFIRM_TIME`.
- **Configuration**: Support parameters via CLI arguments (Miner ID, Auth Key, Temp thresholds, Fan range, intervals).

## Definition of Done
- The script successfully modifies fan speed on the Pitbit website.
- Temperature is kept within or close to the target range.
- The script handles minor network or page load errors gracefully without crashing.
- Documentation (SDD, DECISIONS) accurately reflects the current state of the codebase.

# BioTime API Integration

This application integrates with the BioTime API to manage employee check-ins.

## Features

- Fetches employee check-in data from BioTime API.
- Updates local database with fetched data.
- Handles pagination from the API response.
- Updates the last synced ID for efficient data fetching.

## Installation

bench get-app https://github.com/splinter-NGoH/BioTime-API-Integration.git

bench --site sitename install-app biotime_api_integration

bench migrate

## License

MIT
## v0.20.3 (2026-07-02)

### fix

- **config**: unify on ENVIRONMENT, fix poe api target, default OpenBB to prod
- **ci**: add Redis service and required env vars to test workflow
- **ci**: replace broken devcontainer-based test workflow with uv, fix resulting test failures
- apply CodeRabbit auto-fixes
- **config**: unify on ENVIRONMENT, fix poe api target, default OpenBB to prod

## v0.20.2 (2025-05-22)

### 🐛🚑️ Fixes

- **Dockerfile**: using a multistage build

## v0.20.1 (2025-05-22)

### 🐛🚑️ Fixes

- **Dockerfile**: added another dockerfile logic to test

## v0.20.0 (2025-05-22)

### ✨ Features

- **Dockerfile**: updated dockerfile to use uv

## v0.19.0 (2025-05-22)

### ✨ Features

- **bump**: triggering bump

## v0.18.1 (2025-05-12)

### 🐛🚑️ Fixes

- **deps**: bumped humblDATA, still running into typing error

## v0.18.0 (2025-04-30)

## v0.17.0 (2025-04-30)

## v0.16.7 (2025-04-29)

## v0.16.6 (2025-04-24)

## v0.16.5 (2025-04-17)

## v0.16.4 (2025-04-17)

## v0.16.3 (2025-04-16)

## v0.16.2 (2025-04-16)

## v0.16.1 (2025-04-16)

### 🐛🚑️ Fixes

- **test**: adding automatic version bumping to FastAPI app

## v0.16.0 (2025-04-16)

### ✨ Features

- **endpoints**: updated humbl_channel and humbl_momentum

### 📌➕⬇️➖⬆️ Dependencies

- **humbldata**: updated to fix plotly encoding bug

## v0.15.1 (2025-02-25)

### 🐛🚑️ Fixes

- **dockerfile**: install poetry export plugin in the dockerfile

## v0.15.0 (2025-02-24)

### ✨ Features

- **deploy**: updating URL to deploy

## v0.14.4 (2025-02-24)

### 📌➕⬇️➖⬆️ Dependencies

- **update**: humbldata update
- **update**: humbldata
- **uupdate**: updated humbldata with multiple bug fixes

## v0.14.3 (2024-12-02)

### 🐛🚑️ Fixes

- **humbl_compass**: added custom_data to PlotlyTrace object

### 📌➕⬇️➖⬆️ Dependencies

- **update**: humbldata

## v0.14.2 (2024-12-02)

### 🐛🚑️ Fixes

- **humbl_compass**: added latest_humbl_regime to both chart and non-chart responses

### 📌➕⬇️➖⬆️ Dependencies

- **update**: humbldata
- **update**: humbldata now can parse quarterly CPI & CLI data

## v0.14.1 (2024-11-30)

### 🐛🚑️ Fixes

- **humblDATA**: updated humldata with stricter reqs

### 📌➕⬇️➖⬆️ Dependencies

- **update**: new humbldata with bug fixes for obb data collection
- **update**: bum humbldata to 1.11.1
- **update**: humbldata and others

## v0.14.0 (2024-11-29)

### ✨ Features

- **humbl_compass**: adding latest_humbl_regime

### 📌➕⬇️➖⬆️ Dependencies

- **update**: humbldata
- **update**: humbldata

## v0.13.0 (2024-11-18)

### ✨ Features

- **humblCHANNEL**: added membership param

### 📌➕⬇️➖⬆️ Dependencies

- **humbldata**: updated the package for new validation for membership

## v0.12.3 (2024-11-14)

### ♻️ Refactorings

- **rename**: changed cache namespcace for user-table

## v0.12.2 (2024-11-14)

### ♻️ Refactorings

- **rename**: renamed portfolio test

## v0.12.1 (2024-11-14)

### ♻️ Refactorings

- **rename**: changed membership names; changed mandelbrot-channel

## v0.12.0 (2024-10-17)

### ✨ Features

- **humblCOMPASS**: added membership parameter

### 📌➕⬇️➖⬆️ Dependencies

- **humblDATA**: updated package

## v0.11.1 (2024-10-16)

### ♻️ Refactorings

- **toolbox**: compiled all toolbox routers to be imported into one router

## v0.11.0 (2024-10-16)

### ✨ Features

- **humblCOMPASS**: new endpoint, added pydantic models and router

### 📌➕⬇️➖⬆️ Dependencies

- **humblDATA**: updated package

## v0.10.0 (2024-10-01)

### ✨ Features

- **LICENSE**: added license

## v0.9.0 (2024-09-24)

### ✨ Features

- **CORSMiddleware**: expose headers accessible to browser
- **logging**: added loggign for lifespan app setup

### build

- **deps**: bump redis from 5.0.7 to 5.0.8

## v0.8.0 (2024-08-07)

### ✨ Features

- **error-catching**: added cleaner errors for user-table/

## v0.7.0 (2024-08-06)

### ✨ Features

- **HumblResponse**: added standard response to portfolio for user_table

## v0.6.0 (2024-08-05)

### ✨ Features

- **HumblResponse**: standardize response object for all routes

### 🐛🚑️ Fixes

- **mandelbrot-channel**: added return type hint
- **mandelbrot_channel**: fixed typing for HumblResponse
- **mandelbrot-channel**: return type of route can be validated with chart=True

### 📌➕⬇️ ➖⬆️  Dependencies

- **fastapi-limiter**: adding rate limiting package

## v0.5.0 (2024-07-31)

### ✨ Features

- **utils**: function to delete all REDIS keys that match a pattern
- **redis-routes**: added redis DB routes: flushing and health test
- **env**: added properties to control the prod.dev environment and flags
- **last-close**: added Pydantic Response Model
- **default_response_model**: now using  as default response class
- **middleware**: adding gzip middleware compression
- **fastapi-cache**: user-table/ route cached
- **fastapt-cache**: mandelbro-channel/ route is caching successfully

### 🐛🚑️ Fixes

- **user-table**: fixing namespace cache name
- **returning raw dicts to work with **: ...
- **import**: HTTPException from FastAPI

### ✅🤡🧪 Tests

- **openbb**: added test for openbb endpoints

### 📌➕⬇️ ➖⬆️  Dependencies

- **add**: orjson

## v0.4.0 (2024-07-23)

### ✨ Features

- **openbb**: added /last-close/ route to get yesterdays close price
- **openbb**: added /latest-price/ route to collect an assets most recent price

### 🐛🚑️ Fixes

- **mandelbro_channel**: added all parameters to the function, same access as

## v0.3.1 (2024-07-20)

### 🐛🚑️ Fixes

- **deps**: removed deps controlled in humbldata
- **user_table**: changed param froom  -->
- **user_table**: using  or route queries as suggested in FastAPI docs

### ✅🤡🧪 Tests

- **routers**: add simple router root tests
- **app**: adding health endpoint test

### 📌➕⬇️ ➖⬆️  Dependencies

- **poetry**: update
- **update**: humbldata=1.6.4, polars=1.1.0, python=3.12.4, openbb=4.3
- **upgrade**: fastAPI

## v0.3.0 (2024-07-09)

### ✨ Features

- **logger**: added  function

### 🐛🚑️ Fixes

- **middleware**: added url path and method to logging middleware

## v0.2.2 (2024-07-07)

### 🐛🚑️ Fixes

- **main.py**: added CORS MIddleware

## v0.2.1 (2024-07-07)

## v0.2.0 (2024-07-07)

### ✨ Features

- **UserTable**: adds a parametrized route for  to collect portfolio

### ci

- **deps**: bump docker/build-push-action from 5 to 6
- **deps**: bump codecov/codecov-action from 3 to 4

## v0.1.0 (2024-07-05)

### ✨ Features

- **api-router**: router import fixed, now can access  data!!
- **init**: commit init

### 🐛🚑️ Fixes

- **DO**: attempting to use pip install

### ✅🤡🧪 Tests

- **null**: null commit to test auto-deploy on DO

from fastapi import APIRouter

from humblapi.api.v1.routers.toolbox import (
    humbl_channel,
    humbl_compass,
    humbl_momentum,
)

# Create an instance of the Toolbox APIRouter
# Specified prefix and tags defined here
router = APIRouter(tags=["toolbox"])

# Include the router for humbl_channel, allowing access to its endpoints
router.include_router(humbl_channel.router)

# Include the router for humbl_compass, allowing access to its endpoints
router.include_router(humbl_compass.router)

router.include_router(humbl_momentum.router)

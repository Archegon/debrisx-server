from .router import api_router

@api_router.get("/training/take_picture")
async def start_camera():
    """
    Take a picture with the camera
    """
    # Sends command to client to take a picture
    # Receives picture from client
    # save pictures to a directory
    # return the path to the picture
    # return response with path and success message
    return {"message": "Camera started"}

@api_router.get("/training/{picture_id}")
async def get_picture(picture_id: int):
    """
    Get a picture by ID
    """
    # return the picture with the given id
    return {"message": "Picture received"}

@api_router.delete("/training/{picture_id}")
async def delete_picture(picture_id: int):
    """
    Delete a picture by ID
    """
    # delete the picture with the given id
    return {"message": "Picture deleted"}
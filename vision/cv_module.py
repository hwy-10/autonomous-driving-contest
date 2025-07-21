def get_cv_status(frame) -> Status:
    
    lane_center = get_lane_center(frame)
    
    if lane_center < 280:
        return Status.left
    
    elif lane_center > 360:
        return Status.right
    
    else:
        return Status.go
    
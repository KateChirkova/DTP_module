@router.post("/v1/detections")
async def detections(request: DetectionRequest):  # bbox, confidence, geo
    # 1. Создать Detection
    detection = Detection(**request.dict())
    db.add(detection)

    # 2. Найти/создать Accident (IoU bbox)
    accident = find_or_create_accident(detection)

    # 3. WebSocket уведомление
    if accident.is_new:
        broadcast_new_accident(accident)

    db.commit()
    return {"success": True, "accident_id": accident.id}
from ultralytics import YOLO

def main():
    model = YOLO('yolov8n.pt')

    model.train(
        data='coco_custom.yaml',
        epochs=5,
        imgsz=640,
        batch=10,
        name='final',
        device='cuda',  
        verbose=True
    )

    results = model.val()
    print(results)


if __name__ == '__main__':
    main()
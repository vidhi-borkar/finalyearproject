import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import torch

class YoloHumanDetector(Node):
    def __init__(self):
        super().__init__('yolo_human_detector')
        self.sub = self.create_subscription(Image, '/image_raw', self.callback, 10)
        self.bridge = CvBridge()
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.model.classes = [0]  # Class 0 = person
        self.get_logger().info('YOLOv5 Human Detector Initialized')

    def callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(frame)
        annotated = results.render()[0]
        cv2.imshow('YOLO Human Detection', annotated)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = YoloHumanDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


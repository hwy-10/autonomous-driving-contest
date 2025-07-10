#include <opencv2/opencv.hpp>
#include <iostream>
#include <filesystem>
#include <chrono>

namespace fs = std::filesystem;
using namespace cv;
using namespace std;
using namespace std::chrono;

int main() {
    const int THRESHOLD_VAL = 160;
    const int CANNY_LOW = 20;
    const int CANNY_HIGH = 150;
    const int FIXED_WHITE_X = 320;
    const int Y_TARGET = 390;
    const int MAX_IDX = 54;

    Scalar HSV_LOWER(0, 0, 200);
    Scalar HSV_UPPER(180, 50, 255);
    Mat kernel = getStructuringElement(MORPH_RECT, Size(5, 5));

    fs::create_directories("after_pict");

    int i = 1;
    while (1 <= i && i <= MAX_IDX) {
        auto total_start = high_resolution_clock::now();

        // 이미지 로드
        auto start = high_resolution_clock::now();
        string image_path = "pict/frame(" + to_string(i) + ").jpg";
        Mat frame = imread(image_path);
        if (frame.empty()) {
            cout << "Failed to load image: " << image_path << endl;
            i++;
            continue;
        }
        cout << "[이미지 로드] " << duration<double, milli>(high_resolution_clock::now() - start).count() << " ms\n";

        // HSV 마스크
        start = high_resolution_clock::now();
        resize(frame, frame, Size(640, 480));
        Mat hsv, hsv_mask, hsv_result;
        cvtColor(frame, hsv, COLOR_BGR2HSV);
        inRange(hsv, HSV_LOWER, HSV_UPPER, hsv_mask);
        bitwise_and(frame, frame, hsv_result, hsv_mask);
        cout << "[HSV 마스크] " << duration<double, milli>(high_resolution_clock::now() - start).count() << " ms\n";

        // 그레이스케일 및 마스킹
        start = high_resolution_clock::now();
        Mat gray, gray_masked;
        cvtColor(hsv_result, gray, COLOR_BGR2GRAY);
        gray_masked = Mat::zeros(gray.size(), gray.type());
        gray(Rect(0, gray.rows / 2, gray.cols, gray.rows / 2)).copyTo(
            gray_masked(Rect(0, gray.rows / 2, gray.cols, gray.rows / 2)));
        cout << "[그레이스케일 필터링] " << duration<double, milli>(high_resolution_clock::now() - start).count() << " ms\n";

        // 형태학적 필터링
        start = high_resolution_clock::now();
        Mat morph;
        morphologyEx(gray_masked, morph, MORPH_CLOSE, kernel);
        morphologyEx(morph, morph, MORPH_OPEN, kernel);
        imshow("before", morph);
        erode(morph, morph, kernel, Point(-1, -1), 1);
        imshow("after", morph);
        cout << "[형태학적 필터링] " << duration<double, milli>(high_resolution_clock::now() - start).count() << " ms\n";

        // 이진화 + 엣지
        start = high_resolution_clock::now();
        Mat binary, edges, filled;
        threshold(morph, binary, THRESHOLD_VAL, 255, THRESH_BINARY);
        vector<vector<Point>> contours;
        findContours(binary, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
        filled = Mat::zeros(binary.size(), CV_8UC1);
        drawContours(filled, contours, -1, Scalar(255), FILLED);
        Canny(filled, edges, CANNY_LOW, CANNY_HIGH);
        cout << "[이진화 + 엣지] " << duration<double, milli>(high_resolution_clock::now() - start).count() << " ms\n";

        // 중점 계산 및 표시
        start = high_resolution_clock::now();
        Mat edges_colored;
        cvtColor(edges, edges_colored, COLOR_GRAY2BGR);
        vector<int> white_indices;

        for (int x = 0; x < edges.cols; x++) {
            if (edges.at<uchar>(Y_TARGET, x) == 255) {
                white_indices.push_back(x);
            }
        }

        if (white_indices.size() >= 2) {
            int x_left = white_indices.front();
            int x_right = white_indices.back();
            int mid_x = (x_left + x_right) / 2;

            string direction = (FIXED_WHITE_X - mid_x > 0) ? "left" : "right";

            circle(edges_colored, Point(mid_x, Y_TARGET), 5, Scalar(0, 0, 255), -1);
            putText(edges_colored, direction, Point(30, 60), FONT_HERSHEY_SIMPLEX,
                    1.5, Scalar(0, 255, 0), 3, LINE_AA);
        }

        circle(edges_colored, Point(FIXED_WHITE_X, Y_TARGET), 5, Scalar(255, 255, 255), -1);
        cout << "[중점 처리 시간] " << duration<double, milli>(high_resolution_clock::now() - start).count() << " ms\n";

        // 이미지 저장
        string output_path = "after_pict/frame(" + to_string(i) + ")_edge.jpg";
        imwrite(output_path, edges_colored);

        // 전체 처리 시간
        cout << "[전체 처리 시간] " << duration<double, milli>(high_resolution_clock::now() - total_start).count() << " ms\n\n";

        // 시각화
        imshow("Original", frame);
        imshow("Canny Edge", edges_colored);

        int key = waitKey(0);
        if (key == 27) break;             // ESC
        else if (key == 'a' && i > 1) i--; // 이전 이미지
        else if (key == 'd' && i < MAX_IDX) i++; // 다음 이미지
    }

    destroyAllWindows();
    return 0;
}

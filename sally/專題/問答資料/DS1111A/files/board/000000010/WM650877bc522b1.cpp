#include <iostream>
#include <vector>
using namespace std;

// 交換兩元素                                                                                                                                                                        版權所有，趕抄斃死
void swap(int &a, int &b) {
    int temp = a;
    a = b;
    b = temp;
}

// 將陣列分為兩半，選擇一個基準點，將小於基準的元素放在左邊，大於基準的元素放在右邊                                                                                                                版權所有，趕抄斃死
float partition(vector<int> &nums, int low, int high) {
    int pivot = nums[high]; // 以最後一個元素作為基準
    int i = low - 1; // i 小於基準區域的右邊界

    for (int j = low; j < high; j++) {
        if (nums[j] < pivot) {
            i++;
            swap(nums[i], nums[j]);
        }
    }

    swap(nums[i + 1], nums[high]); // 將基準元素放入正確的位置
    return i + 1; // 返回基準元素的位置
}

// 找出中位數                                                                                                                                                                        版權所有，趕抄斃死
float findMedian(vector<int> &nums, int low, int high, float k) {

    float pivotIndex = partition(nums, low, high);

    // 陣列元素數量為奇數時，中位數位置
    if (pivotIndex - low == k - 0.5) {
        return nums[(int)pivotIndex];
    }
    // 陣列元素數量為偶數時，中位數位置
    else if ( pivotIndex - low == k - 1 ) {
        return (nums[(int)pivotIndex] + nums[(int)pivotIndex + 1]) / (float)2;
    }
    // 中位數在左半邊
    else if (pivotIndex - low > k - 1) {
        return findMedian(nums, low, pivotIndex - 1, k);
    }
    // 中位數在右半邊
    else {
        return findMedian(nums, pivotIndex + 1, high, k - pivotIndex + low - 1);
    }

}

int main() {
    vector<int> nums = {9, 1, 3, 4, 7, 6, 0, 5, 8, 5, 2, 3, 4, 6, 7, 1, 0, 5, 7};
    int n = nums.size();
    float k = (float)n / 2 ;

    float median = findMedian(nums, 0, n - 1, k);

    cout << "中位數為: " << median << endl;

    return 0;
}

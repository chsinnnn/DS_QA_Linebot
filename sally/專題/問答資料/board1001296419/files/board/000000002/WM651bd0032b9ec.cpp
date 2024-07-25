// 11127137, 黃乙家
#include <bits/stdc++.h>
#include <chrono>
using namespace std;

class Solution {
public:
  vector<vector<int>> threeSum(vector<int> &nums,
                               int target) { // Brute Force, O(n^3)
    if (nums.empty() || nums.size() < 3) // 不到三個數字，沒有答案
      return {};
    int n = nums.size();
    sort(nums.begin(), nums.end()); // 先排序好 平均：O(nlogn)，最差：O(n^2)
    vector<vector<int>> ret;
    for (int i = 0; i < n - 2; i++) {
      if (i == 0 || nums[i] != nums[i - 1]) { // 去掉重複的數字
        for (int j = i + 1; j < n - 1; j++) {
          if (j == i + 1 || nums[j] != nums[j - 1]) {
            for (int k = j + 1; k < n; k++) {
              if (k == j + 1 || nums[k] != nums[k - 1]) {
                if (nums[i] + nums[j] + nums[k] == target) {
                  ret.push_back({nums[i], nums[j], nums[k]});
                }
              }
            }
          }
        }
      }
    }

    return ret;
  }

  vector<vector<int>> threeSum2(vector<int> &nums,
                                int target) { // hash table, O(n^2)
    if (nums.empty() || nums.size() < 3)
      return {};
    int n = nums.size();
    sort(nums.begin(), nums.end());
    vector<vector<int>> ret;
    unordered_map<int, int> mp; // hash table
    for (int i = 0; i < n; i++) {
      mp[nums[i]] = i;
    }
    for (int i = 0; i < n - 2; i++) {
      if (i == 0 || nums[i] != nums[i - 1]) { // 去掉重複的數字
        for (int j = i + 1; j < n - 1; j++) {
          if (j == i + 1 || nums[j] != nums[j - 1]) {
            int t = target - nums[i] - nums[j];
            if (mp.find(t) != mp.end() && mp[t] > j) { // 找到且不重複
              ret.push_back({nums[i], nums[j], t});
            }
          }
        }
      }
    }
    return ret;
  }
  vector<vector<int>> threeSum3(vector<int> &nums,
                                int target) { // Two Pointers, O(n^2)
    if (nums.empty() || nums.size() < 3)
      return {};
    int n = nums.size();
    sort(nums.begin(), nums.end());
    vector<vector<int>> ret;
    for (int i = 0; i < n - 2; i++) {
      if (i == 0 || nums[i] != nums[i - 1]) {
        int l = i + 1, r = n - 1;

        while (l < r) {
          if (nums[i] + nums[l] + nums[r] == target) {
            ret.push_back({nums[i], nums[l], nums[r]});
            while (l < r && nums[l] == nums[l + 1]) // 去掉重複的數字
              l++;
            while (l < r && nums[r] == nums[r - 1])
              r--;
            l++;
            r--;
          } else if (nums[i] + nums[l] + nums[r] < target) {
            l++;
          } else
            r--;
        }
      }
    }
    return ret;
  }
};

int main() {
  Solution S;
  vector<int> nums;
  int n;
  cin >> n;
  for (int i = 0; i < n; i++) {
    int t;
    cin >> t;
    nums.push_back(t);
  }
  int target;
  cin >> target;
  auto start = chrono::steady_clock::now();
  vector<vector<int>> ans = S.threeSum(nums, target);
  auto end = chrono::steady_clock::now();
  chrono::duration<double> elapsed_seconds = end - start;
  for (auto i : ans) {
    for (auto j : i) {
      cout << j << ' ';
    }
    cout << endl;
  }
  cout << fixed << "Brute Force Time: " << (double)elapsed_seconds.count()
       << endl;

  start = chrono::steady_clock::now();
  ans = S.threeSum2(nums, target);
  end = chrono::steady_clock::now();
  elapsed_seconds = end - start;
  cout << fixed << "Hash table Time: " << (double)elapsed_seconds.count()
       << endl;

  start = chrono::steady_clock::now();
  ans = S.threeSum3(nums, target);
  end = chrono::steady_clock::now();
  elapsed_seconds = end - start;
  cout << fixed << "Two Pointers Time: " << (double)elapsed_seconds.count()
       << endl;
}
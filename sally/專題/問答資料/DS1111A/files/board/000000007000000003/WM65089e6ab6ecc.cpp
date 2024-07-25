// 11127137, 黃乙家
// If Chinese text cannot normally displays, please view this program with
// UTF-8.
/****************************************************/
/*  CPP Template for School                         */
/*  Author: CompileErr0r(YiJia)                     */
/*  Author ID: 11127137                             */
/*  Compile Environment: Windows 11 64bit MingW-GCC */
/*  Compiler: g++ 9.4                               */
/****************************************************/

#ifdef CONSTOPT

#pragma GCC optimize("Ofast")
#pragma loop_opt(on)
// #pragma GCC optimize("Ofast,unroll-loops,no-stack-protector,fast-math")
// #pragma GCC target("sse,sse2,sse3,ssse3,sse4,popcnt,abm,mmx,avx")
#pragma comment(linker, "/stack:200000000")

#endif

// #include <bits/stdc++.h>

#include <algorithm>
#include <bitset>
#include <cassert>
#include <cctype>
#include <cmath>
#include <complex>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <deque>
#include <exception>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <istream>
#include <iterator>
#include <list>
#include <map>
#include <memory>
#include <new>
#include <numeric>
#include <ostream>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <utility>
#include <valarray>
#include <vector>

using namespace std;

struct BigInteger {
  string num;
  int sign;
  int size() { return num.size(); }
  BigInteger() {}
  BigInteger RemoveLeadingZero(int nsign) { // 去掉前導零
    sign = nsign;
    for (int i = num.size() - 1; i > 0 && num[i] == '0'; i--) {
      num.pop_back();
    }
    if (num.size() == 1 && num[0] == '0') { // 0 的符號為正
      sign = 1;
    }
    return *this;
  }
  BigInteger operator=(string s) {
    num = (s[0] == '-' ? s.substr(1) : s);
    reverse(num.begin(), num.end());
    (*this).RemoveLeadingZero(s[0] == '-' ? -1 : 1);
    return *this;
  }

  BigInteger(string s) { *this = s; }
  BigInteger(long long x) { (*this) = to_string(x); }
  BigInteger operator=(long long x) {
    (*this) = to_string(x);
    return *this;
  }
  bool operator==(BigInteger y) { return num == y.num && sign == y.sign; }
  bool operator==(long long y) { return (*this) == BigInteger(y); }
  bool operator==(string y) { return (*this) == BigInteger(y); }
  bool operator!=(BigInteger y) { return !((*this) == y); }
  bool operator!=(long long y) { return !((*this) == y); }
  bool operator!=(string y) { return !((*this) == y); }
  bool operator<(BigInteger y) {
    if (sign != y.sign) { // 符號不同，直接比較就好
      return sign < y.sign;
    }
    if (num.size() != y.num.size()) { // 位數不同，位數多的數字大
      return num.size() * sign < y.num.size() * y.sign;
    }
    for (int i = num.size() - 1; i >= 0; i--) {
      if (num[i] != y.num[i]) {
        return num[i] * sign < y.num[i] * y.sign;
      }
    }
    return false; // 相等
  }
  bool operator<(long long y) { return (*this) < BigInteger(y); }
  bool operator<(string y) { return (*this) < BigInteger(y); }
  bool operator>(BigInteger y) { return y < (*this); }
  bool operator>(long long y) { return (*this) > BigInteger(y); }
  bool operator>(string y) { return (*this) > BigInteger(y); }
  bool operator<=(BigInteger y) { return !((*this) > y); }
  bool operator<=(long long y) { return (*this) <= BigInteger(y); }
  bool operator<=(string y) { return (*this) <= BigInteger(y); }
  bool operator>=(BigInteger y) { return !((*this) < y); }
  bool operator>=(long long y) { return (*this) >= BigInteger(y); }
  bool operator>=(string y) { return (*this) >= BigInteger(y); }
  BigInteger operator+(BigInteger y) { // 模擬直式加法
    if (sign != y.sign) {
      return (*this) - (-y);
    }
    BigInteger ans;
    ans.sign = sign;
    for (int i = 0, carry = 0; i < size() || i < y.size() || carry; i++) {
      if (i < size()) {
        carry += num[i] - '0';
      }
      if (i < y.size()) {
        carry += y.num[i] - '0';
      }
      ans.num += (carry % 10 + '0');
      carry /= 10;
    }
    return ans.RemoveLeadingZero(sign);
  }
  BigInteger operator+(long long y) { return (*this) + BigInteger(y); }
  BigInteger operator+(string y) { return (*this) + BigInteger(y); }
  BigInteger operator+=(BigInteger y) { return (*this) = (*this) + y; }
  BigInteger operator+=(long long y) { return (*this) = (*this) + y; }
  BigInteger operator+=(string y) { return (*this) = (*this) + y; }
  BigInteger operator-() {
    BigInteger ans = (*this);
    ans.sign = -sign;
    return ans;
  }
  BigInteger operator-(BigInteger y) { // 減法，與加法類似
    if (sign != y.sign) {
      return (*this) + (-y);
    }
    if ((*this) < y) {
      return -(y - (*this));
    }
    BigInteger ans;
    ans.sign = sign;
    for (int i = 0, carry = 0; i < size(); i++) {
      carry += num[i] - '0';
      if (i < y.size()) {
        carry -= y.num[i] - '0';
      }
      if (carry < 0) {
        ans.num += (carry + 10 + '0');
        carry = -1;
      } else {
        ans.num += (carry + '0');
        carry = 0;
      }
    }
    return ans.RemoveLeadingZero(sign);
  }
  BigInteger operator-(long long y) { return (*this) - BigInteger(y); }
  BigInteger operator-(string y) { return (*this) - BigInteger(y); }
  BigInteger operator-=(BigInteger y) { return (*this) = (*this) - y; }
  BigInteger operator-=(long long y) { return (*this) = (*this) - y; }
  BigInteger operator-=(string y) { return (*this) = (*this) - y; }
  BigInteger operator*(
      BigInteger
          y) { // 直式乘法，O(N^2)，可以用Karatsuba算法或快速傅立葉轉換加速
    BigInteger ans("0");

    for (int i = 0, k = 0; i < size(); i++, k++) {
      int carry = 0; // 進位
      for (int j = 0; j < y.size() || carry; j++) {
        if (j < y.size()) { // 一般乘法
          carry += (num[i] - '0') * (y.num[j] - '0');
        }
        if (k + j < ans.size()) { // 發生進位
          carry += ans.num[k + j] - '0';
        }
        if (k + j >= ans.size()) { // 補位
          ans.num += (carry % 10 + '0');
        } else {
          ans.num[k + j] = (carry % 10 + '0');
        }
        carry /= 10;
      }
    }
    return ans.RemoveLeadingZero(sign * y.sign);
  }
  BigInteger operator*(long long y) { return (*this) * BigInteger(y); }
  BigInteger operator*(string y) { return (*this) * BigInteger(y); }
  BigInteger operator*=(BigInteger y) { return (*this) = (*this) * y; }
  BigInteger operator*=(long long y) { return (*this) = (*this) * y; }
  BigInteger operator*=(string y) { return (*this) = (*this) * y; }
  BigInteger operator/(BigInteger y) { // 直式除法
    if (y.size() == 1 && y.num[0] == '0') {
      throw runtime_error("Divide by zero exception");
    }
    BigInteger ans, cur("0");
    for (int i = 0; i < size(); ++i)
      ans.num += '0';
    int nsign = sign * y.sign;
    y.sign = 1;
    for (int i = size() - 1; i >= 0; i--) {
      cur.num.insert(cur.num.begin(), '0');
      cur = cur + num.substr(i, 1);
      while (cur >= y) {
        cur = cur - y;
        ans.num[i]++;
      }
    }
    return ans.RemoveLeadingZero(nsign);
  }
  BigInteger operator/(long long y) { return (*this) / BigInteger(y); }
  BigInteger operator/(string y) { return (*this) / BigInteger(y); }
  BigInteger operator/=(BigInteger y) { return (*this) = (*this) / y; }
  BigInteger operator/=(long long y) { return (*this) = (*this) / y; }
  BigInteger operator/=(string y) { return (*this) = (*this) / y; }
  BigInteger operator%(BigInteger y) {
    if (y.size() == 1 && y.num[0] == '0') {
      throw runtime_error("Divide by zero exception");
    }
    BigInteger ans("0");
    int nsign = sign * y.sign;
    y.sign = 1;
    for (int i = size() - 1; i >= 0; i--) {
      ans.num.insert(ans.num.begin(), '0');
      ans = ans + num.substr(i, 1);
      while (ans >= y) {
        ans = ans - y;
      }
    }
    return ans.RemoveLeadingZero(nsign);
  }
  BigInteger operator%(long long y) { return (*this) % BigInteger(y); }
  BigInteger operator%(string y) { return (*this) % BigInteger(y); }
  BigInteger operator%=(BigInteger y) { return (*this) = (*this) % y; }
  BigInteger operator%=(long long y) { return (*this) = (*this) % y; }
  BigInteger operator%=(string y) { return (*this) = (*this) % y; }
  BigInteger operator++() { return (*this) = (*this) + 1; }
  BigInteger operator++(int) {
    BigInteger temp = (*this);
    (*this) = (*this) + 1;
    return temp;
  }
  BigInteger operator--() { return (*this) = (*this) - 1; }
  BigInteger operator--(int) {
    BigInteger temp = (*this);
    (*this) = (*this) - 1;
    return temp;
  }
  friend ostream &operator<<(ostream &os, BigInteger &x) { // 定義怎麼輸出
    if (x.sign == -1) {
      os << '-';
    }
    for (int i = x.num.size() - 1; i >= 0; i--) {
      os << x.num[i];
    }
    return os;
  }
  friend istream &operator>>(istream &is, BigInteger &x) { // 定義怎麼輸入
    string s;
    is >> s;
    x = s;
    return is;
  }

  static BigInteger pow(BigInteger x,
                        BigInteger y) { // 為求速度，使用快速冪算法
    BigInteger ans = 1;
    while (y > 0) {
      if (y % 2 == 1) {
        ans *= x;
      }
      x *= x;
      y /= 2;
    }
    return ans;
  }

  static BigInteger Karatsuba(BigInteger x, BigInteger y) { // Karatsuba算法
    if (x.size() < y.size()) {
      return Karatsuba(y, x);
    }
    if (x.size() == 1) {
      return x * y;
    }
    int n = x.size();
    int mid = n / 2;
    BigInteger a = x / BigInteger(pow(10, mid)); // 取被乘數的前半部
    BigInteger b = x % BigInteger(pow(10, mid)); // 取被乘數的後半部
    BigInteger c = y / BigInteger(pow(10, mid)); // 取乘數的前半部
    BigInteger d = y % BigInteger(pow(10, mid)); // 取乘數的後半部
    BigInteger ac = Karatsuba(a, c);             // 前半部相乘
    BigInteger bd = Karatsuba(b, d);             // 後半部相乘
    BigInteger abcd = Karatsuba(a + b, c + d);
    // 計算 (a + b) * (c + d) = ac + ad + bc + bd
    // 上式減掉 ac 和 bd 就是 ad + bc(在這裡減少乘法步驟了)
    // x * y = (a*10^mid + b) * (c*10^mid + d)
    // = ac * 10^(2*mid) + (ad + bc) * 10^mid + bd
    return ac * BigInteger(pow(10, 2 * mid)) +
           (abcd - ac - bd) * BigInteger(pow(10, mid)) + bd;
  }
};

int main() {
  BigInteger a, b;
  cout << "\nInput the first BigInteger(a) > ";
  cin >> a;
  cout << "\nInput the second BigInteger(b) > ";
  cin >> b;
  BigInteger c = a + b;
  cout << "a + b = " << c << "\n";
  c = a - b;
  cout << "a - b = " << c << "\n";
  c = a * b;
  cout << "a * b = " << c << "\n";
  c = BigInteger::Karatsuba(a, b);
  cout << "(Karatsuba) a * b = " << c << "\n";
  try {
    c = a / b;
    cout << "a / b = " << c << "\n";
    c = a % b;
    cout << "a % b = " << c << "\n";
  } catch (exception &e) {
    cout << e.what() << "\n";
  }
  bool d = a == b;
  cout << "(a == b) = " << (d ? "true" : "false") << "\n";
  d = a != b;
  cout << "(a != b) = " << (d ? "true" : "false") << "\n";
  d = a < b;
  cout << "(a < b) = " << (d ? "true" : "false") << "\n";
  d = a > b;
  cout << "(a > b) = " << (d ? "true" : "false") << "\n";
  return 0;
}

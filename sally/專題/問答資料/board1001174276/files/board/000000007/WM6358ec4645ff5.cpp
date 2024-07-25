#include <iostream>
#include <fstream>
#include <vector>
using namespace std;

int main() {
    /*
    原本有個叫ABC.txt的檔案有三行內容
    我先讀進來存到vector
    再新建一個複製檔，寫入舊資料，並新增三行內容
    註：此程式碼檔案必須與ABC.txt放在同一資料夾
    產生的複製檔也會在此資料夾內
    */
    // 變數宣告
    vector<string> vec ; // 存檔案的每一行
    string nameStr = "ABC.txt"; // 檔案名稱，見附件
    string toStoreStr = ""; // 暫存檔案的每一行

    // ifstream：讀檔
    ifstream toOpen(nameStr.c_str()); // 以讀取模式開啟檔案
    while (getline(toOpen, toStoreStr)) vec.push_back(toStoreStr); // 逐行寫入vector
    toOpen.close(); // 以讀取模式關閉檔案
    cout << "Original file's data :" << endl;
    for (int i = 0; i < vec.size(); i++) cout << vec[i] << endl; // 印出檔案的每一行

    // ofstream：寫檔
    nameStr = "copy" + nameStr;
    ofstream copyFile(nameStr.c_str()); // 建立一個新的複製檔並以寫入模式開啟複製檔
    for (int i = 0; i < vec.size(); i++) copyFile << vec[i] << endl; // 複製舊檔資料到複製檔
    vec.erase(vec.begin(), vec.end()); // 清空重置vector
    for (int i = 0; i < 3; i++) vec.push_back("write : line " + to_string(i+4));
    for (int i = 0; i < vec.size(); i++) copyFile << vec[i] << endl; // 寫入新資料
    copyFile.close(); // 以寫入模式關閉複製檔

    // 印出修改後的內容
    vec.erase(vec.begin(), vec.end()); // 清空重置vector
    toStoreStr = ""; // 清空重置暫存字串
    ifstream openCopyFile(nameStr.c_str()); // 以讀取模式開啟複製檔
    while (getline(openCopyFile, toStoreStr)) vec.push_back(toStoreStr); // 逐行寫入vector
    cout << "Copyed and altered file's data :" << endl;
    for (int i = 0; i < vec.size(); i++) cout << vec[i] << endl; // 印出檔案的每一行
    openCopyFile.close(); // 以讀取模式關閉複製檔

    /*
    執行結果：
    (1)印出以下內容
    Original file's data :
    read : line 1
    read : line 2
    read : line 3
    Copyed and altered file's data :
    read : line 1
    read : line 2
    read : line 3
    write : line 4
    write : line 5
    write : line 6
    (2)產生總計六行資料的複製檔copyABC.txt
    */
} // main()
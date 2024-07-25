#include <iostream>
#include <string>
#include <list>
#include <stack>

using namespace std;

int operator_priority(string& operator_val);
int operator_priority(char op);

enum class nodeType {
    undefined,
    Operator,
    Element
};

enum class read_state {
    Padding, // 表示其處於沒有任何狀態，一般是在處理空白時會處於此模式。接受字元: 物件與物件之間的空白
    Varible, // 表示讀進去的是一個變數，變數名僅允許英文開頭的字元，並僅能由英文字母、數字所構成。 接受字元: A-Z, a-z, 0-9(僅限非開頭位置)
    Operator, // 表示讀進去的是一個運算符，僅允許+、-、*、/
    Number,  // 表示讀進去的是一個整數，僅允許數字、負號
};

class binaryNode {
public:
    binaryNode() { // binaryNode的建構式。
        leftNode = nullptr;
        rightNode = nullptr;
        parentNode = nullptr;
        nodetype = nodeType::undefined;
        value = "";
    }
    void setAsOperator(binaryNode& left, binaryNode& right, string operator_val) { // 將此binaryNode設為一個用來存放運算元的節點。
        if (&left == &right) {
            throw exception("left and right node are same object.");
        }
        left.parentNode = this;
        right.parentNode = this;
        leftNode = &left;
        rightNode = &right;
        value = operator_val;
        nodetype = nodeType::Operator;
    }
    void setAsElement(string value) { // 將此binaryNode設為一個用來存放變數或是數字的節點。
        this->value = value;
        nodetype = nodeType::Element;
    }
    bool isLeftNode() const { // 表示此節點相對於母節點是否為左節點
        if (parentNode != nullptr) {
            if (parentNode->leftNode == this)
                return true;
            else
                return false;
        }
        else {
            return false;
        }
    }
    bool isRightNode() const { // 表示此節點相對於母節點是否為右節點
        if (parentNode != nullptr) {
            if (parentNode->rightNode == this)
                return true;
            else
                return false;
        }
        else {
            return false;
        }
    }
    bool isRootNode() const { // 表示此節點是否為根節點
        return parentNode == nullptr;
    }
    binaryNode* getLeftNode() const { // 取得此節點的左子節點。
        return leftNode;
    }
    binaryNode* getRightNode() const { // 取得此節點的右子節點。
        return rightNode;
    }
    binaryNode* getParentNode() const { // 取得此節點的父節點。
        return parentNode;
    }
    string getValue() const { // 取得目前此節點存放的值。
        return value;
    }
    string toString() { // 以中序表示法表示此節點
        if (this->nodetype == nodeType::Operator) {
            string output = "";
            if (leftNode->nodetype == nodeType::Operator && operator_priority(leftNode->value) < operator_priority(this->value)) { // 表示左子節點的運算優先度比起目前節點還要來的低，所以要加括號，讓他能先被計算。
                output += "(" + leftNode->toString() + ")"; // 
            }
            else { // 表示左子節點的運算優先度比起目前節點還要來的高，所以不用加括號
                output += leftNode->toString();
            }
            output += value; 
            if (rightNode->nodetype == nodeType::Operator && operator_priority(rightNode->value) < operator_priority(this->value)) { // 表示右子節點的運算優先度比起目前節點還要來的低，所以要加括號，讓他能先被計算。
                output += "(" + rightNode->toString() + ")";
            }
            else { // 表示右子節點的運算優先度比起目前節點還要來的高，所以不用加括號
                output += rightNode->toString();
            }
            return output;
        }
        else if (this->nodetype == nodeType::Element) { 
            return value;
        }
        else {
            return "undefined!";
        }
    }
    ~binaryNode() { // binaryNode的解構式。
        delete leftNode;
        delete rightNode;
    }
private: 
    binaryNode* leftNode; // 左子節點的指標
    binaryNode* rightNode; // 右子節點的指標
    binaryNode* parentNode; // 父節點的指標
    nodeType nodetype; // 節點類型
    string value; //值
};

//取得運算元的優先層級，-1表示此字串並非運算元。
int operator_priority(string& operator_val) { 
    if (operator_val.size() != 1)
        return -1;
    char op = operator_val[0];
    switch (op) {
        case '+': case '-':
            return 1;
        case '*': case '/':
            return 2;
        default:
            return -1;
    }
}

//取得運算元的優先層級，-1表示此字元並非運算元。
int operator_priority(char op) { 
    switch (op) {
        case '+': case '-':
            return 1;
        case '*': case '/':
            return 2;
        default:
            return -1;
    }
}

//用來將string_builder轉成字串。
string string_builder_output(list<char> &string_builder) { 
    char* buffer = new char[string_builder.size() + 1];
    int index = 0;
    for (auto ch : string_builder) {
        buffer[index++] = ch;
    }
    buffer[string_builder.size()] = '\0';
    string output = string(buffer);
    delete[] buffer;
    return output;
}

// 建樹函式，輸入的後序表示法以空白隔開，
binaryNode* building_tree(string postorder_expression) {
    list<char> string_builder = list<char>(); // 此Linked list是用來分割時保存字元的用途，
    stack<binaryNode *> building_stack = stack<binaryNode *>(); // 用來處理建樹的堆疊
    read_state current_read_state = read_state::Padding;
    char last_read_char = '\0';
    int pos = 0;
    postorder_expression += " "; //在結尾加上一個空白讓原本最後一個字元能夠處理完。
    for (auto ch : postorder_expression) {
        pos++;
        if (current_read_state == read_state::Padding) {
            if (isspace(ch) || postorder_expression.size() == pos)
                continue;
            if (isalpha(ch)) { // 變數
                current_read_state = read_state::Varible;
                string_builder.push_back(ch);
            }
            else if (operator_priority(ch)) {  // 符號
                current_read_state = read_state::Operator;
                string_builder.push_back(ch);
            }
            else if (isdigit(ch)) { // 數字
                current_read_state = read_state::Number;
                string_builder.push_back(ch);
            }
            else {
                cerr << "func[building_tree]: unexcepted character: " << ch << ". at" << pos << "." << endl;
                throw exception("unexcepted character.");
            }
        }
        else if (current_read_state == read_state::Varible) { //處理 變數物件
            if (isspace(ch) || postorder_expression.size() == pos) {
                string ele_val = string_builder_output(string_builder);
                binaryNode* ele_node = new binaryNode();
                ele_node->setAsElement(ele_val);
                building_stack.push(ele_node);
                current_read_state = read_state::Padding;
                string_builder.clear();
            }
            else if (!isalnum(ch)) {
                cerr << "func[building_tree]: unexcepted character: " << ch << ". at" << pos << "." << endl;
                throw exception("unexcepted character.");
            }
            else {
                string_builder.push_back(ch);
            }
        }
        else if (current_read_state == read_state::Number) { //處理 數字物件
            if (isspace(ch) || postorder_expression.size() == pos) {
                string ele_val = string_builder_output(string_builder);
                binaryNode* ele_node = new binaryNode();
                ele_node->setAsElement(ele_val);
                building_stack.push(ele_node);
                current_read_state = read_state::Padding;
                string_builder.clear();
            }
            else if (!isdigit(ch)) {
                cerr << "func[building_tree]: unexcepted character: " << ch << ". at" << pos << "." << endl;
                throw exception("unexcepted character.");
            }
            else {
                string_builder.push_back(ch);
            }
        }
        else if (current_read_state == read_state::Operator) { //處理 運算元 物件
            if (isspace(ch) || postorder_expression.size() == pos) {
                string ele_val = string_builder_output(string_builder);
                if (building_stack.size() < 2) {
                    cerr << "func[building_tree]: operator " << ele_val << "required 2 arguments." << endl;
                    throw exception("unexcepted character.");
                }
                else {
                    binaryNode* right_node = building_stack.top();
                    building_stack.pop();
                    binaryNode* left_node = building_stack.top();
                    building_stack.pop();
                    binaryNode* ope_ele = new binaryNode();
                    ope_ele->setAsOperator(*left_node, *right_node, ele_val);
                    building_stack.push(ope_ele);
                    current_read_state = read_state::Padding;
                    string_builder.clear();
                }
            }
            else if (isdigit(ch) && last_read_char == '-') { //因「-」預設將其歸類為減法運算元，所以在此狀態如果讀到數字，前一個字元又是「-」的話，表示「-」應該當作負號來看，而非運算元。
                current_read_state = read_state::Number;
                string_builder.push_back(ch);
            }
            else if (operator_priority(ch) == -1) {
                cerr << "func[building_tree]: unexcepted character: " << ch << ". at" << pos << "." << endl;
                throw exception("unexcepted character.");
            }
            else {
                string_builder.push_back(ch);
            }
        }
        last_read_char = ch; 
    }
    if (building_stack.empty()) { //因為只有Padding狀態不會對building_stack壓入新的元素，所以若是building_stack為空，表示輸入字串內不包含任何能被解析的後序表示式。
        cerr << "func[building_tree]: no any legal postfix expression in input string can be parsed."<< endl;
        throw exception("no any legal postfix expression in input string can be parsed.");
    }
    else if (building_stack.size() > 1) { //表示此運算式缺乏部分運算元，需要更多運算元才能完成運算
        cerr << "func[building_tree]: input string is illegal postfix expression. some operator isn't given." << endl;
        throw exception("input string is illegal postfix expression. some operator isn't given.");
    }
    binaryNode* result = building_stack.top(); //將building_stack堆疊頂的元素取出，同時因此時building_stack只有一個元素，所以building_stack在取出後會為空。
    building_stack.pop();
    return result;
}

int main() {
    try {
        binaryNode* node = building_tree("a b + c * d e + f * + w z + *");
        string expression = node->toString();
        cout << "output: " << expression << endl;
        delete node;
    }
    catch (exception& ex) {
        cerr << "Error: " << ex.what() << endl;
    }
    system("pause");
    return 0;
}

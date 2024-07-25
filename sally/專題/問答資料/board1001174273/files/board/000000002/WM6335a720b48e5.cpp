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

class binaryNode {
public:
    binaryNode() {
        leftNode = nullptr;
        rightNode = nullptr;
        parentNode = nullptr;
        nodetype = nodeType::undefined;
        value = "";
    }
    void setAsOperator(binaryNode& left, binaryNode& right, string operator_val) {
        left.parentNode = this;
        right.parentNode = this;
        leftNode = &left;
        rightNode = &right;
        value = operator_val;
        nodetype = nodeType::Operator;
    }
    void setAsElement(string value) {
        this->value = value;
        nodetype = nodeType::Element;
    }
    bool isLeftNode() const {
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
    bool isRightNode() const {
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
    bool isParentNode() const {
        return parentNode == nullptr;
    }
    binaryNode* getLeftNode() const {
        return leftNode;
    }
    binaryNode* getRightNode() const {
        return rightNode;
    }
    binaryNode* getParentNode() const {
        return parentNode;
    }
    string getValue() const {
        return value;
    }
    string toString() {
        binaryNode* cur_node = this;
        if (this->nodetype == nodeType::Operator) {
            string output = "";
            if (leftNode->nodetype == nodeType::Operator && operator_priority(leftNode->value) < operator_priority(this->value)) {
                output += "(" + leftNode->toString() + ")";
            }
            else {
                output += leftNode->toString();
            }
            output += value;
            if (rightNode->nodetype == nodeType::Operator && operator_priority(rightNode->value) < operator_priority(this->value)) {
                output += "(" + rightNode->toString() + ")";
            }
            else {
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
    ~binaryNode() {
        delete leftNode;
        delete rightNode;
    }
private:
    binaryNode* leftNode;
    binaryNode* rightNode;
    binaryNode* parentNode;
    nodeType nodetype;
    string value;
};

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

binaryNode* building_tree(string postorder_expression) {
    list<char> string_builder = list<char>();
    stack<binaryNode *> building_stack = stack<binaryNode *>();
    for (auto ch : postorder_expression) {
        if (ch == ' ' || ch == '\n' || ch == '\0') {
            if (string_builder.size() > 0) {
                string outputStr = string_builder_output(string_builder);
                string_builder.clear();
                if (operator_priority(outputStr) != -1) {
                    binaryNode* new_operator_obj = new binaryNode();
                    binaryNode& right_node = *building_stack.top();
                    building_stack.pop();
                    binaryNode& left_node = *building_stack.top();
                    building_stack.pop();
                    new_operator_obj->setAsOperator(left_node, right_node, outputStr);
                    building_stack.push(new_operator_obj);
                }
                else {
                    binaryNode* new_ele_obj = new binaryNode();
                    new_ele_obj->setAsElement(outputStr);
                    building_stack.push(new_ele_obj);
                }
            }
        }
        else{
            string_builder.push_back(ch);
        }
    }
    if (string_builder.size() > 0) {
        string outputStr = string_builder_output(string_builder);
        if (operator_priority(outputStr) != -1) {
            binaryNode* new_operator_obj = new binaryNode();
            binaryNode& right_node = *building_stack.top();
            building_stack.pop();
            binaryNode& left_node = *building_stack.top();
            building_stack.pop();
            new_operator_obj->setAsOperator(left_node, right_node, outputStr);
            building_stack.push(new_operator_obj);
        }
        else {
            binaryNode* new_ele_obj = new binaryNode();
            new_ele_obj->setAsElement(outputStr);
            building_stack.push(new_ele_obj);
        }
    }
    binaryNode* result = building_stack.top();
    return result;
}

int main() {
    binaryNode* node = building_tree("a b + c * d e + f * + w z + *");
    string expression = node->toString();
    cout << "output: " << expression << endl;
    system("pause");
    delete node;
    return 0;
}

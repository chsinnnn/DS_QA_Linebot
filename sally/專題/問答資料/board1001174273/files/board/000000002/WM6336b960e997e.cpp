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
    Padding, // ��ܨ�B��S�����󪬺A�A�@��O�b�B�z�ťծɷ|�B�󦹼Ҧ��C�����r��: ����P���󤧶����ť�
    Varible, // ���Ū�i�h���O�@���ܼơA�ܼƦW�Ȥ��\�^��}�Y���r���A�öȯ�ѭ^��r���B�Ʀr�Һc���C �����r��: A-Z, a-z, 0-9(�ȭ��D�}�Y��m)
    Operator, // ���Ū�i�h���O�@�ӹB��šA�Ȥ��\+�B-�B*�B/
    Number,  // ���Ū�i�h���O�@�Ӿ�ơA�Ȥ��\�Ʀr�B�t��
};

class binaryNode {
public:
    binaryNode() { // binaryNode���غc���C
        leftNode = nullptr;
        rightNode = nullptr;
        parentNode = nullptr;
        nodetype = nodeType::undefined;
        value = "";
    }
    void setAsOperator(binaryNode& left, binaryNode& right, string operator_val) { // �N��binaryNode�]���@�ӥΨӦs��B�⤸���`�I�C
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
    void setAsElement(string value) { // �N��binaryNode�]���@�ӥΨӦs���ܼƩάO�Ʀr���`�I�C
        this->value = value;
        nodetype = nodeType::Element;
    }
    bool isLeftNode() const { // ��ܦ��`�I�۹����`�I�O�_�����`�I
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
    bool isRightNode() const { // ��ܦ��`�I�۹����`�I�O�_���k�`�I
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
    bool isRootNode() const { // ��ܦ��`�I�O�_���ڸ`�I
        return parentNode == nullptr;
    }
    binaryNode* getLeftNode() const { // ���o���`�I�����l�`�I�C
        return leftNode;
    }
    binaryNode* getRightNode() const { // ���o���`�I���k�l�`�I�C
        return rightNode;
    }
    binaryNode* getParentNode() const { // ���o���`�I�����`�I�C
        return parentNode;
    }
    string getValue() const { // ���o�ثe���`�I�s�񪺭ȡC
        return value;
    }
    string toString() { // �H���Ǫ�ܪk��ܦ��`�I
        if (this->nodetype == nodeType::Operator) {
            string output = "";
            if (leftNode->nodetype == nodeType::Operator && operator_priority(leftNode->value) < operator_priority(this->value)) { // ��ܥ��l�`�I���B���u���פ�_�ثe�`�I�٭n�Ӫ��C�A�ҥH�n�[�A���A���L����Q�p��C
                output += "(" + leftNode->toString() + ")"; // 
            }
            else { // ��ܥ��l�`�I���B���u���פ�_�ثe�`�I�٭n�Ӫ����A�ҥH���Υ[�A��
                output += leftNode->toString();
            }
            output += value; 
            if (rightNode->nodetype == nodeType::Operator && operator_priority(rightNode->value) < operator_priority(this->value)) { // ��ܥk�l�`�I���B���u���פ�_�ثe�`�I�٭n�Ӫ��C�A�ҥH�n�[�A���A���L����Q�p��C
                output += "(" + rightNode->toString() + ")";
            }
            else { // ��ܥk�l�`�I���B���u���פ�_�ثe�`�I�٭n�Ӫ����A�ҥH���Υ[�A��
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
    ~binaryNode() { // binaryNode���Ѻc���C
        delete leftNode;
        delete rightNode;
    }
private: 
    binaryNode* leftNode; // ���l�`�I������
    binaryNode* rightNode; // �k�l�`�I������
    binaryNode* parentNode; // ���`�I������
    nodeType nodetype; // �`�I����
    string value; //��
};

//���o�B�⤸���u���h�šA-1��ܦ��r��ëD�B�⤸�C
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

//���o�B�⤸���u���h�šA-1��ܦ��r���ëD�B�⤸�C
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

//�ΨӱNstring_builder�ন�r��C
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

// �ؾ�禡�A��J����Ǫ�ܪk�H�ťչj�}�A
binaryNode* building_tree(string postorder_expression) {
    list<char> string_builder = list<char>(); // ��Linked list�O�ΨӤ��ήɫO�s�r�����γ~�A
    stack<binaryNode *> building_stack = stack<binaryNode *>(); // �ΨӳB�z�ؾ𪺰��|
    read_state current_read_state = read_state::Padding;
    char last_read_char = '\0';
    int pos = 0;
    postorder_expression += " "; //�b�����[�W�@�Ӫť����쥻�̫�@�Ӧr������B�z���C
    for (auto ch : postorder_expression) {
        pos++;
        if (current_read_state == read_state::Padding) {
            if (isspace(ch) || postorder_expression.size() == pos)
                continue;
            if (isalpha(ch)) { // �ܼ�
                current_read_state = read_state::Varible;
                string_builder.push_back(ch);
            }
            else if (operator_priority(ch)) {  // �Ÿ�
                current_read_state = read_state::Operator;
                string_builder.push_back(ch);
            }
            else if (isdigit(ch)) { // �Ʀr
                current_read_state = read_state::Number;
                string_builder.push_back(ch);
            }
            else {
                cerr << "func[building_tree]: unexcepted character: " << ch << ". at" << pos << "." << endl;
                throw exception("unexcepted character.");
            }
        }
        else if (current_read_state == read_state::Varible) { //�B�z �ܼƪ���
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
        else if (current_read_state == read_state::Number) { //�B�z �Ʀr����
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
        else if (current_read_state == read_state::Operator) { //�B�z �B�⤸ ����
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
            else if (isdigit(ch) && last_read_char == '-') { //�]�u-�v�w�]�N���k������k�B�⤸�A�ҥH�b�����A�p�GŪ��Ʀr�A�e�@�Ӧr���S�O�u-�v���ܡA��ܡu-�v���ӷ�@�t���ӬݡA�ӫD�B�⤸�C
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
    if (building_stack.empty()) { //�]���u��Padding���A���|��building_stack���J�s�������A�ҥH�Y�Obuilding_stack���šA��ܿ�J�r�ꤺ���]�t�����Q�ѪR����Ǫ�ܦ��C
        cerr << "func[building_tree]: no any legal postfix expression in input string can be parsed."<< endl;
        throw exception("no any legal postfix expression in input string can be parsed.");
    }
    else if (building_stack.size() > 1) { //��ܦ��B�⦡�ʥF�����B�⤸�A�ݭn��h�B�⤸�~�৹���B��
        cerr << "func[building_tree]: input string is illegal postfix expression. some operator isn't given." << endl;
        throw exception("input string is illegal postfix expression. some operator isn't given.");
    }
    binaryNode* result = building_stack.top(); //�Nbuilding_stack���|�����������X�A�P�ɦ]����building_stack�u���@�Ӥ����A�ҥHbuilding_stack�b���X��|���šC
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

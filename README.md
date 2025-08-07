# CIE ALEVEL 9168 Computer Science Pseudocode Interpreter
## 1. Overall Introduction
This is an interpreter created by Huiheng Li, a former CIE CS self-taught student
It can be used to interprete Pseudocode written in the syntax defined according to 2026 CIE 9618 CS pseudocode guide.
Hope this will be helpful to CIE CS study and teaching :-)
## 2. Technical Introduction
 - **Developing language(with version)**: Python 3.11.9
 - **External Libs requirement**: **None**(no external libs are required)
## 3. Features and Functions
 - Comments
 - Error handling
 - Data Types Declaring
    - INTEGER
    - REAL
    - CHAR
    - STRING
    - BOOLEAN
    - DATE
 - Assigning
    - Single Value
    - Expression
 - Array Declaring and Using
    - 1D Array
    - 2D Array
 - User-defined data types Declaring and Using
 - Pointer Declaring and Using
 - Input
 - Output
 -  Arithmetic operations
 - Relational operations
 - Logic operators(forgot in the v1.0, will be updated)
 - String functions and operations
 - Numeric functions
 - Selection
    - IF selection
    - CASE OF selection
 - Iteration(repetition)
    - Count-controlled (FOR) loops
    - Post-condition (REPEAT) loops
    - Pre-condition (WHILE) loops
 - Procedures and functions
    - Defining and calling procedures
    - Defining and calling functions
    -  Passing parameters by value or by reference
 - File handling(forgot in the v1.0, will be updated)
 - Object-oriented Programming(forgot in the v1.0, will be updated)
## How to use?
1. ensure you have Python installed in your device and it's 3.11.9 or above
2. first clone this Repository to local environment
```bash
git clone https://github.com/你的用户名/仓库名.git
```
3. then create a folder called "scripts" under "app" folder and a python script file, name it as you want 
4. open the python script file with the tool software you like(VSCODE or PYCHARM or other things)
5. paste the following code in it
```python
from app.evaluator.tokenizer import tokenize
from app.parser.parser import Parser
from app.evaluator.interpreter import Interpreter

code = """
code here
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.eval(ast)
```
6. replace the **"code here"** with your pseudocode, save the file
7. open terminal and use **cd** instruction to enter this folder
```bash
cd this_folder
```
8. then enter instruction to see the result
```bash
python -m scripts.your_file
```
9. Generally speaking the program passed all the function tests(except the functions that I forgot to accomplish), which means it doesn't suppose to fail with simple programs(I haven't test it with a complex program so it is possible to see a problem that doesn't relate with you). if you meet any unsolveable problem or bugs, please submit it at **GitHub Issues**, this will be really helpful for me to upgrade the tool. 
## Contribution
I might not figure out some of the bugs, if you find them out, please feel free to submit it at **GitHub Issues**!
## Donation
If you think my program is good, you can buy me a coffee! This will encourage me! Thanks
<img style="width:40%;" src="https://s2.loli.net/2023/06/09/eFHIZ1NpDhoAUnb.png"/>
# License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
You may modify and redistribute this project non-commercially under the same license, with proper attribution.

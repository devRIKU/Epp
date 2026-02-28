# E++ Reference Guide

E++ (English Plus Plus) is an English-first language where code reads and writes like natural sentences. The only punctuation allowed in code syntax are commas `,` and periods `.`. It is fully Turing Complete and suitable for real programming tasks!

## 1. Variables
Variables dynamically store numbers, text (`"..."`), lists, booleans (`true`/`false`), and objects.
```
set age to 25.
set name to "Alice".
set is ready to true.

set colors to list of "red", "green".
```

## 2. Input and Output
```
say "Hello World.".
say "Your age is", age.

ask "What is your name?" and store in name.
```

## 3. Expressions & Math
E++ supports standard mathematical and logical operators natively:
`+`, `-`, `*`, `/`, `>`, `<`, `>=`, `<=`, `==`, `!=`, `=`, `and`, `or`, `not`.

You can also concatenate strings organically!
```
set price to 10 * 5.
set is adult to age >= 18.
set greeting to "Hello " joined with name.
```

## 4. Conditionals
Conditionals execute logically based on standard English blocks.
```
if age >= 18 then.
    say "Adult".
otherwise if age >= 13 then.
    say "Teen".
otherwise.
    say "Child".
end if.
```

## 5. Loops
E++ has `repeat`, `while`, and `for each` loops.
```
repeat 5 times.
    say "Looping...".
end repeat.

while score > 0.
    set score to score - 1.
end while.

for each color in colors.
    say color.
end for.
```

## 6. Collections (Lists)
```
set fruits to list of "apple", "banana".
add "grape" to fruits.
remove "apple" from fruits.

say item 1 of fruits.
say size of fruits.
```

## 7. Functions
Functions can return values using `give back`. Call them inline with `call`.
```
define add with a, b.
    give back a + b.
end define.

set total to call add with 10, 20.
```

## 8. Records (Objects)
Create basic key-value entities!
```
set person to record.
    set person name to "Alice".
    set person age to 30.
end record.

say person name.
```

## 9. Error Handling
Recover gracefully without crashing.
```
try.
    set x to 10 / 0.
on error.
    say "Something broke!".
end try.
```

## 10. Standard Built-Ins
E++ gives you immediate access to helpful system utilities out of the box!
- `call square root of x`
- `call round x`
- `call absolute of x`
- `call length of x`
- `call uppercase of "hello"`
- `call lowercase of "HELLO"`
- `call sort list x`
- `call reverse list x`

## 11. Type Checking
Use natural inline type checks for dynamic validation.
```
set num check to check if 100 is a number.
set str check to check if "hello" is a string.
set bool check to check if true is a boolean.
```

## 12. Multi-line Strings
You can create strings that span multiple lines using `text block`.
```
set big doc to text block
    These lines
    will be safely saved
    with their line breaks intact!
end text.

say big doc.
```

## 13. File I/O Operations
Read and write to the disk using organic English.
```
write "Hello file!" to file "data.txt".
read file "data.txt" into my content.
say my content.
```

## 14. Real-time Interactive Shell (REPL)
To drop into the interactive environment to experiment with statements on the fly natively in your terminal, simply run the interpreter without providing a file parameter!
```bash
python epp_interpreter.py 
```
Type `exit.` or `quit.` anytime to leave!

## 15. Webview Windows (GUI)
E++ has a built-in native window system powered by `pywebview`. You can create desktop GUI windows and render HTML inside them!

### Create a Window
```
create window titled "My App".
```

### Set Inline HTML Content
```
set window content of "My App" to "<h1>Hello E++!</h1>".
```

### Load a Local HTML File
```
create window titled "Welcome".
load file "welcome.html" into window "Welcome".
show windows.
```

### Open a URL (Mini Browser)
```
create window titled "Browser".
open url "https://example.com" in window "Browser".
show windows.
```

### Custom Window Size
```
create window titled "Dashboard" sized 1024 by 768.
```

> **Important:** Always call `show windows.` as the last statement to start the window event loop.

## 16. HTML Reader & Web Fetcher
E++ can fetch web pages and extract their readable text — no external libraries needed!

### Fetch a Web Page
```
fetch page "https://example.com" into raw html.
say raw html.
```

### Extract Text from HTML
```
fetch page "https://example.com" into raw html.
read text from html raw html into clean text.
say clean text.
```

### Read a Local HTML File
```
read html file "page.html" into content.
say content.
```

## 17. Pseudo Code Support
E++ can also parse and execute **standard pseudo code** syntax! This makes it easy to translate textbook algorithms directly into runnable E++ programs. All pseudo code keywords are case-insensitive.

### Comments
```
// This is a pseudo code comment.
```

### Variable Declaration
```
DECLARE x = 10.
DECLARE name = "Alice".
DECLARE count AS INTEGER.
DECLARE greeting AS STRING.
DECLARE items AS ARRAY.
DECLARE flag AS BOOLEAN.
```
Supported types: `INTEGER`, `INT`, `FLOAT`, `REAL`, `DOUBLE`, `STRING`, `CHAR`, `BOOLEAN`, `BOOL`, `ARRAY`.

### Assignment
```
ASSIGN 42 TO count.
ASSIGN x = 10.
x <- 100.
```

### Output
```
PRINT "Hello World".
OUTPUT x.
DISPLAY "Result: ", result.
```

### Input
```
INPUT name.
READ age.
INPUT value WITH PROMPT "Enter a number:".
```

### Functions and Procedures
```
FUNCTION add(a, b)
    RETURN a + b.
END FUNCTION.

PROCEDURE greet(name)
    PRINT "Hello, ", name.
END PROCEDURE.

CALL add(3, 5).
```

### Conditionals
```
IF x > 10 THEN
    PRINT "big".
ELSEIF x > 5 THEN
    PRINT "medium".
ELSE
    PRINT "small".
ENDIF.
```

### For Loops
```
FOR i = 1 TO 10
    PRINT i.
NEXT.

FOR i = 0 TO 20 STEP 5
    PRINT i.
NEXT.
```

### While Loops
```
WHILE x > 0 DO
    PRINT x.
    DECREMENT x.
ENDWHILE.
```

### Do-Until / Do-While
```
DO
    PRINT x.
    INCREMENT x.
UNTIL x > 10.

DO
    PRINT x.
    DECREMENT x.
LOOP WHILE x > 0.
```

### Switch / Case
```
SWITCH grade
    CASE "A"
        PRINT "Excellent!".
    CASE "B"
        PRINT "Good".
    DEFAULT
        PRINT "Try harder".
ENDSWITCH.
```

### Increment / Decrement
```
INCREMENT counter.
DECREMENT counter.
INCREMENT score BY 10.
DECREMENT health BY 5.
```

### Swap
```
SWAP a AND b.
```

### Block Markers
```
BEGIN
    // code here
END.
```

### Control Flow
```
BREAK.
CONTINUE.
EXIT.
```

> **Tip:** You can freely mix E++ English syntax and pseudo code syntax in the same program!

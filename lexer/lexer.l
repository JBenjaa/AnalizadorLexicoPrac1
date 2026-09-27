%{
#include <stdio.h>
#include <stdlib.h>

int linea = 1;
%}

%option noyywrap

%%

"int"       { printf("KEYWORD|%s|%d\n", yytext, linea); }
"float"     { printf("KEYWORD|%s|%d\n", yytext, linea); }
"string"    { printf("KEYWORD|%s|%d\n", yytext, linea); }
"bool"      { printf("KEYWORD|%s|%d\n", yytext, linea); }

"if"        { printf("KEYWORD|%s|%d\n", yytext, linea); }
"else"      { printf("KEYWORD|%s|%d\n", yytext, linea); }
"while"     { printf("KEYWORD|%s|%d\n", yytext, linea); }
"print"     { printf("KEYWORD|%s|%d\n", yytext, linea); }

"true"      { printf("BOOLEAN|%s|%d\n", yytext, linea); }
"false"     { printf("BOOLEAN|%s|%d\n", yytext, linea); }

[0-9]+\.[0-9]+ {
    printf("FLOAT|%s|%d\n", yytext, linea);
}

[0-9]+ {
    printf("INTEGER|%s|%d\n", yytext, linea);
}

[a-zA-Z_][a-zA-Z0-9_]* {
    printf("IDENTIFIER|%s|%d\n", yytext, linea);
}

\"([^\"\\]|\\.)*\" {
    printf("STRING|%s|%d\n", yytext, linea);
}

"==" {
    printf("EQUAL|%s|%d\n", yytext, linea);
}

"!=" {
    printf("NOT_EQUAL|%s|%d\n", yytext, linea);
}

">=" {
    printf("GREATER_EQUAL|%s|%d\n", yytext, linea);
}

"<=" {
    printf("LESS_EQUAL|%s|%d\n", yytext, linea);
}

">" {
    printf("GREATER|%s|%d\n", yytext, linea);
}

"<" {
    printf("LESS|%s|%d\n", yytext, linea);
}

"=" {
    printf("ASSIGN|%s|%d\n", yytext, linea);
}

"+" {
    printf("PLUS|%s|%d\n", yytext, linea);
}

"-" {
    printf("MINUS|%s|%d\n", yytext, linea);
}

"*" {
    printf("MULTIPLY|%s|%d\n", yytext, linea);
}

"/" {
    printf("DIVIDE|%s|%d\n", yytext, linea);
}

"(" {
    printf("LPAREN|%s|%d\n", yytext, linea);
}

")" {
    printf("RPAREN|%s|%d\n", yytext, linea);
}

"{" {
    printf("LBRACE|%s|%d\n", yytext, linea);
}

"}" {
    printf("RBRACE|%s|%d\n", yytext, linea);
}

";" {
    printf("SEMICOLON|%s|%d\n", yytext, linea);
}

"," {
    printf("COMMA|%s|%d\n", yytext, linea);
}

"//".* {
    /* Ignorar comentarios */
}

[ \t\r]+ {
    /* Ignorar espacios */
}

\n {
    linea++;
}

. {
    printf("ERROR|%s|%d\n", yytext, linea);
}

%%

int main()
{
    yylex();
    return 0;
}
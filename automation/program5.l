%{
#include "y.tab.h"
#include <stdlib.h>
#include <string.h>
%}

DIGIT  [0-9]
ID     [a-zA-Z][a-zA-Z0-9]*
WS     [ \t\n]
STRING \"[^"]*\"

%%
"int"      { return INT; }
"main"     { return MAIN; }
"printf"   { return PRINTF; }
"return"   { return RETURN; }

{STRING}   { yylval.str = strdup(yytext); return STRING; }
{DIGIT}+   { yylval.num = atoi(yytext); return NUM; }
{ID}       { yylval.id = strdup(yytext); return ID; }

"+"        { return ADD; }
"="        { return ASSIGN; }
"("        { return LPAREN; }
")"        { return RPAREN; }
";"        { return SEMI; }
","        { return COMMA; }
"{"        { return LBRACE; }
"}"        { return RBRACE; }

{WS}       ;   /* ignore whitespace */

%%

int yywrap() {
    return 1;
}

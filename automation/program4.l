%{
#include "y.tab.h"
%}

%%
[0-9]+ { yylval.sym = yytext[0]; return NUMBER; }
[a-zA-Z] { yylval.sym = yytext[0]; return LETTER; }
\n  { return 0; }
[ \t]  ;
. { return yytext[0]; }
%%

int yywrap() { return 1; }

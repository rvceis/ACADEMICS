%{
#include <stdio.h>
#include <stdlib.h>

struct incod {
    char opd1, opd2, opr;
} code[20];

int ind = 0;
char temp = 'T';

char AddToTable(char, char, char);
void generateCode();
%}


%union { char sym; }
%token <sym> LETTER NUMBER
%type <sym> expr

%left '+' '-'
%left '*' '/'

%%

statement:
    LETTER '=' expr ';' {
        AddToTable($1, $3, '=');
    }
  | expr ';'
;

expr:
    expr '+' expr { $$ = AddToTable($1, $3, '+'); }
  | expr '-' expr { $$ = AddToTable($1, $3, '-'); }
  | expr '*' expr { $$ = AddToTable($1, $3, '*'); }
  | expr '/' expr { $$ = AddToTable($1, $3, '/'); }
  | '(' expr ')'  { $$ = $2; }
  | NUMBER        { $$ = $1; }
  | LETTER        { $$ = $1; }
;

%%

char AddToTable(char opd1, char opd2, char opr) {
    code[ind] = (struct incod){opd1, opd2, opr};
    char result = temp;
    temp++;   // next temp variable
    ind++;
    return result;
}

void generateCode() {
    printf("\nThree Address Code:\n");
    for (int i = 0; i < ind; i++) {
        if (i == ind - 1)
            printf("%c %c %c\n", code[i].opd1, code[i].opr, code[i].opd2);
        else
            printf("T%d = %c %c %c\n", i, code[i].opd1, code[i].opr, code[i].opd2);
    }

    printf("\nQuadruple Code:\n");
    for (int i = 0; i < ind; i++) {
        if (i == ind - 1)
            printf("%d\t%c\t%c\t%c\n", i, code[i].opr, code[i].opd1, code[i].opd2);
        else
            printf("%d\t%c\t%c\t%c\tT%d\n", i, code[i].opr, code[i].opd1, code[i].opd2, i);
    }

    printf("\nTriple Code:\n");
    for (int i = 0; i < ind; i++) {
        printf("%d\t%c\t%c\t%c\n", i, code[i].opr, code[i].opd1, code[i].opd2);
    }
}

int main() {
    printf("Enter expression (e.g., a=b+c;):\n");
    yyparse();
    generateCode();
    return 0;
}

int yyerror(char *s) {
    printf("Error: %s\n", s);
    return 0;
}


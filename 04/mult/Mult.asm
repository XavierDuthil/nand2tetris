// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[3], respectively.)

// Put your code here.

@1
D=M		// Charge l'opérande droite dans le registre D
@15		// On stocke dans R15
M=D     // $R15 = $R1

@2
M=0     // Flush $R2 (résultat)

(LOOP)
    @15
    D=M     // D = $R15
    @END
    D;JLE   // if (D < 0) goto END (vérification de fin de boucle)

    @0
	D=M     // D = $R0 (on charge R0)
    @2
    M=D+M   // $R2 += $R0 (résultat += opérande gauche)

    @15
    M=M-1   // $R15 -= 1

    @LOOP
    0;JMP   // Goto LOOP

(END)
    @END
    0;JMP   // Boucle infinie
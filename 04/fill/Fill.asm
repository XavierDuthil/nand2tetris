// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.

@8192
D=A
@0
M=D		// i = 8192 (variable de boucle)

@SCREEN
D=A
@1
M=D		// printAddress = @SCREEN

(MAINLOOP)
	@24576
	D=M
	@PRINTWORD
	D;JNE   // if(keyDown) PRINTWORD()
	
	@ERASEWORD
    0;JMP   // else ERASEWORD()

(PRINTWORD)
	@1
	D=M
	@24575
	D=D-A
	@MAINLOOP
	D;JGT   	// if(printAddress <= maxPrintAdress)

	@1
	A=M
	M=-1	// print(printAddress)

	@1
	M=M+1	// printAddress++
	
	@MAINLOOP
    0;JMP   // Goto MAINLOOP
	
(ERASEWORD)
	@1
	D=M
	@SCREEN
	D=D-A
	@MAINLOOP
	D;JLT   	// if(printAddress >= @SCREEN)

	@1
	A=M
	M=0		// erase(printAddress)

	@1
	M=M-1	// printAddress--
	
	@MAINLOOP
    0;JMP   // Goto MAINLOOP
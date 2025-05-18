MODULE Module1
    CONST robtarget HOME:=[[465,0,577],[0.5,0.5,-0.5,-0.5],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR num xoffs := 0;
    VAR num yoffs := 0;
    VAR num zoffs := 0;

    PROC Megfog()
        PulseDO DO10_2;
        WaitTime 1;
    ENDPROC
    
    PROC Elenged()
        PulseDO DO10_1;
        WaitTime 1;
    ENDPROC  
    PROC FutoszalagIndit()
        SetDO DO10_3, 1;
        WaitTime 1;
    ENDPROC
    PROC FutoszalagStop()
        SetDO DO10_3, 0;
        WaitTime 1;
    ENDPROC

    PROC main()
    MoveJ Offs(HOME,xoffs,yoffs,zoffs),v10,fine,MyNewTool\WObj:=wobj0;
    !MoveJ Offs(HOME,0,0,0),v10,fine,MyNewTool\WObj:=wobj0;
    ENDPROC
ENDMODULE
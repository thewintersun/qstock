#Include <GuiTab.au3>
#include <GuiButton.au3>


Func RunMain()
   ; 请配置通达信软件的主程序
   Local $iPID = Run("D:\axzq_v6\TdxW.exe", "")
   ; 请配置通达信软件的标题
   Local $title = "[TITLE:安信安睿终端V7.11; CLASS:#32770]"
   WinActivate($title)
   Local $hLoginWnd = WinWaitActive($title)


   ; 开始下载数据
   Sleep(500)
   ControlClick($hLoginWnd, "", "[CLASS:AfxWnd42; INSTANCE:12]")
EndFunc


Func PopDownloadDlg()
   ; 找到主窗口，并弹出下载对话框
   Local $title = "[CLASS:TdxW_MainFrame_Class]"
   WinActivate($title)
   Local $hMainWnd = WinWaitActive($title)
   SendKeepActive($hMainWnd)
   WinMove($hMainWnd, "", 0, 0, 300, 600)


   ;在本地居然不能用，不然会出错
   ;Sleep(2000)
   ;WinClose("[TITLE:即时播报; CLASS:#32770]")


   ; 点击到盘后数据下载
   ; 如果使用Mouse without Borders这个软件进行多台电脑会出错
   ControlClick($hMainWnd, "", 3000)
   ControlClick($hMainWnd, "", "[CLASS:AfxWnd42; INSTANCE:7]")
   Send('{DOWN 11}{ENTER}')
EndFunc


Func SetCheckDownloadDlg()
   ; 点击进行下载
   Local $title = "[TITLE:盘后数据下载; CLASS:#32770]"
   WinActivate($title)
   Local $hDlgWnd = WinWaitActive($title)




   ; 将第一页的日线数据选上
   Sleep(500)
   Local $idRdo1 = ControlGetHandle($hDlgWnd,"","[TEXT:日线和实时行情数据]")
   Local $idRdo2 = ControlGetHandle($hDlgWnd,"","[TEXT:5分钟线数据]")
   Local $idRdo3 = ControlGetHandle($hDlgWnd,"","[TEXT:1分钟线数据]")
   _GUICtrlButton_SetCheck($idRdo1)
   ; 将第二页的5分钟数据选上

   _GUICtrlButton_SetCheck($idRdo2)

   ; 将第二页的1分钟数据选上

   _GUICtrlButton_SetCheck($idRdo3)

   ; 激活各页，需要设置的时间进行切换
   Local $idTab = ControlGetHandle($hDlgWnd,"","[CLASS:SysTabControl32; INSTANCE:1]")
   _GUICtrlTab_SetCurFocus($idTab, 1)
   _GUICtrlTab_SetCurFocus($idTab, 0)
   _GUICtrlTab_SetCurFocus($idTab, 1)
EndFunc


Func ClickDownloadDlg()
   Local $title = "[TITLE:盘后数据下载; CLASS:#32770]"
   WinActivate($title)
   Local $hDlgWnd = WinWaitActive($title)


   ; 开始下载数据
   Sleep(500)
   ControlClick($hDlgWnd, "", "[TEXT:开始下载]")
EndFunc




Func WaitDownloadDlg()

   ; 开始下载数据
   Sleep(500)
   Local $title = "[TITLE:盘后数据下载; CLASS:#32770]"
   WinActivate($title)
   Local $hDlgWnd = WinWaitActive($title)


   Local $idtext = ''
   Do
  Sleep(2000)
  $idtext = ControlGetText($hDlgWnd,"","[CLASS:Static; INSTANCE:3]")
   Until '下载完毕.' = $idtext
   ;Until '下载被取消.' = $idtext
   ; 找到下载完毕.

EndFunc


Func ExitMain()
   ; 需要退出下载对话框，否则程序没有完全退出
   Local $title = "[TITLE:盘后数据下载; CLASS:#32770]"
   WinActivate($title)
   Local $hDlgWnd = WinWaitActive($title)

   WinClose($hDlgWnd)

  ControlClick($hDlgWnd, "", "[TEXT:关闭]")

   Sleep(500)


   ; 关闭主窗口
   Local $title = "[CLASS:TdxW_MainFrame_Class]"
   WinActivate($title)
   Local $hMainWnd = WinWaitActive($title)
   WinClose($hMainWnd)


   ; 确认退出
   Local $hMainWnd = WinWaitActive("[TITLE:退出确认; CLASS:#32770]")
   ControlClick($hMainWnd, "", "[TEXT:退出]")
EndFunc



$i = 0
While $i <= 3

   SetCheckDownloadDlg()

   ClickDownloadDlg()
   WaitDownloadDlg()

   Sleep(10000)
   $i = $i + 1
WEnd


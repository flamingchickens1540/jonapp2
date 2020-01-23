all: dep linux windows macos

dep:
	sudo apt install -y webkit2gtk-4.0 gcc-mingw-w64
	go get github.com/zserge/webview

linux:
	GOOS=linux GOARCH=amd64 go build -o jonapp-linux-amd64
	GOOS=linux GOARCH=386 go build -o jonapp-linux-i386

windows:
	GOOS=windows GOARCH=amd64 go build -o jonapp-windows-amd64.exe
	GOOS=windows GOARCH=386 go build -o jonapp-windows-i386.exe

macos:
	GOOS=darwin GOARCH=amd64 go build -o jonapp-macos-amd64
	GOOS=darwin GOARCH=386 go build -o jonapp-macos-i386

#	mkdir -p jonapp-mac.app/Contents/MacOS
#	go build -o jonapp-mac.app/Contents/MacOS/example

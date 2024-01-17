function pickLines(id) {
  const input = document.getElementById(id);
  const output = document.getElementById("output");

  // Split the input into lines
  let lines = input.value.split("\n");

  // Check if there are any lines to cut
  if (lines.length > 0) {
    // Cut the first line
    const firstLine = lines.shift();
    if (id == "input2" || id == "input3") {
      lines = autoMerge(lines);
    }

    // Update the input and output textareas
    input.value = lines.join("\n");
    output.value += firstLine + "\n";
    scrollBottom();
  }
}

function dropLines(id) {
  const input = document.getElementById(id);

  // Split the input into lines
  let lines = input.value.split("\n");

  // Check if there are any lines to cut
  if (lines.length > 0) {
    // Cut the first line and store it in droppedLines
    const droppedLine = lines.shift();
    pushDroppedLines(id, droppedLine);

    if (id == "input2" || id == "input3") {
      lines = autoMerge(lines);
    }
    // Update the input textarea
    input.value = lines.join("\n");
  }
}

// for enabling undo of dropLines, we need to store the dropped lines in a stack
const droppedLines = [];
// [{from: "input1", line: "line1"}, ...] , latest dropped line is at the end of the array
// functions to push and pop from the stack
function pushDroppedLines(from, line) {
  droppedLines.push({ from: from, line: line });
}
function popDroppedLines() {
  return droppedLines.pop();
}
// function to undo the last dropLines
function undoDropLines() {
  // if there are no dropped lines, do nothing
  if (droppedLines.length === 0) {
    return;
  }
  const droppedLine = popDroppedLines();
  const input = document.getElementById(droppedLine.from);
  input.value = droppedLine.line + "\n" + input.value;
}

// scroll the output textarea to the bottom
function scrollBottom() {
  const output = document.getElementById("output");
  output.scrollTop = output.scrollHeight;
}

// after update of input, if the top line is the same as the one in input1, automatically drop it.
function autoMerge(lines) {
  const input1 = document.getElementById("input1");
  const lines1 = input1.value.split("\n");
  if (lines.length > 0 && lines1.length > 0) {
    if (lines[0] == lines1[0]) {
      lines.shift();
    }
  }
  return lines;
}

// scroll the input textarea to the top
function scrollTop() {
  document.getElementById("input1").scrollTop = 0;
  document.getElementById("input2").scrollTop = 0;
  document.getElementById("input3").scrollTop = 0;
}

// copy the output textarea to the clipboard
function copyOutput() {
  const output = document.getElementById("output");
  output.select();
  document.execCommand("copy");
}

// add new line on output textarea
function addNewLine() {
  const output = document.getElementById("output");
  output.value += "\n";
  scrollBottom();
}

document.getElementById("pick1").addEventListener("click", function () {
  pickLines("input1");
});

document.getElementById("drop1").addEventListener("click", function () {
  dropLines("input1");
});

document.getElementById("pick2").addEventListener("click", function () {
  pickLines("input2");
});

document.getElementById("drop2").addEventListener("click", function () {
  dropLines("input2");
});

document.getElementById("pick3").addEventListener("click", function () {
  pickLines("input3");
});

document.getElementById("drop3").addEventListener("click", function () {
  dropLines("input3");
});

document.getElementById("undo").addEventListener("click", function () {
  undoDropLines();
});

document.getElementById("copy-output").addEventListener("click", function () {
  copyOutput();
});

document.getElementById("scroll-top").addEventListener("click", function () {
  scrollTop();
});

// This event listener allows the user to control the picking and dropping of lines from the input textareas using keyboard shortcuts.
// 'j', 'k', and 'l' are used to pick lines from input1, input2, and input3 respectively.
// 'u', 'i', and 'o' are used to drop lines from input1, input2, and input3 respectively.
// Backspace is used to undo the last dropLines.
document
  .getElementById("smallInput")
  .addEventListener("keydown", function (event) {
    if (event.key === "j") {
      pickLines("input1");
    } else if (event.key === "k") {
      pickLines("input2");
    } else if (event.key === "l") {
      pickLines("input3");
    } else if (event.key === "u") {
      dropLines("input1");
    } else if (event.key === "i") {
      dropLines("input2");
    } else if (event.key === "o") {
      dropLines("input3");
    } else if (event.key === "Backspace") {
      undoDropLines();
    } else if (event.key === "Enter") {
      addNewLine();
    }
    event.preventDefault();
  });

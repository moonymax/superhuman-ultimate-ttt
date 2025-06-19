from pydantic import BaseModel
from typing import List, Tuple
from blessed import Terminal

term = Terminal()


"""
1. user inputs a number to play on a board and then again to play on the smaller board
2. other user gets sent to the smaller board depending on which board the first user chose and using input plays an x or an o
3. once a small board is won/lost/drawn a user sent there will be able to choose any board they would like to play on
"""


class SmallBoard(BaseModel):
    squares: List[int]

class Board(BaseModel):
    small_boards: List[SmallBoard]

def blessed_input(
    term: Terminal,
    prompt: str = "",
    initial_text: str = "",
    position: Tuple[int, int] = (-1, -1)
) -> str:
    """
    Provides a line-based input function similar to Python's built-in input(),
    but with precise terminal control using blessed.

    Allows typing, backspace, and left/right arrow key navigation.

    Args:
        term: The blessed Terminal instance.
        prompt: The string prompt to display before the input field.
        initial_text: An optional string to pre-fill the input buffer.
        position: The (row, column) where the prompt and input should begin.
                  If row or column is -1, it will use the current cursor position.
                  Note: It's best practice to explicitly set position for TUIs.

    Returns:
        The string entered by the user.
    """

    # Initialize the input buffer with initial text, using a list for efficient modifications
    const_input_buffer: List[str] = list(initial_text)
    # Initialize the cursor's logical position within the buffer
    cursor_pos_in_buffer: int = len(initial_text)

    # Determine the starting row and column for the input field
    # If -1, blessed's current cursor position will be used.
    # We get it once to ensure consistency if the terminal is resized later.
    const_start_row: int
    const_start_col: int

    if position[0] == -1 or position[1] == -1:
        # Get current cursor position if not explicitly provided
        # Note: This might not be accurate if other prints have occurred right before.
        # Explicit positioning is generally more robust for TUI.
        const_start_row = term.height - 1 # Default to last row
        const_start_col = 0 # Default to first column
    else:
        const_start_row = position[0]
        const_start_col = position[1]

    # Enter cbreak mode to read single keypresses immediately
    # Hide the cursor to draw a custom one or manage its position precisely
    with term.cbreak(), term.hidden_cursor():
        while True:
            # Calculate the absolute display position for the input text
            # This is where the actual typed characters start after the prompt.
            const_input_display_col: int = const_start_col + len(prompt)

            # 1. Clear the line from the start of the prompt to the end of the terminal.
            # This ensures any previous content is removed before redrawing.
            print(term.move(const_start_row, const_start_col) + term.clear_eol, end="")

            # 2. Print the prompt.
            print(prompt, end="")

            # 3. Print the current content of the input buffer.
            # Using "".join(list) is efficient for converting list to string.
            print("".join(const_input_buffer), end="")

            # 4. Position the cursor accurately within the displayed input.
            # The cursor's absolute column is the start of input display + its logical position.
            const_abs_cursor_col: int = const_input_display_col + cursor_pos_in_buffer
            print(term.move(const_start_row, const_abs_cursor_col), end="", flush=True)

            # Read a single key press from the user.
            const_key = term.inkey()

            # Handle different key presses
            if const_key == '\r' or const_key == '\n' or const_key == term.KEY_ENTER:
                # User pressed Enter, input is complete.
                break
            elif const_key == term.KEY_BACKSPACE or const_key == '\x7f':
                # Handle Backspace (ASCII 127, sometimes also '\b')
                if cursor_pos_in_buffer > 0:
                    del const_input_buffer[cursor_pos_in_buffer - 1]
                    cursor_pos_in_buffer -= 1
            elif const_key == term.KEY_DELETE:
                # Handle Delete key (often distinct from backspace)
                if cursor_pos_in_buffer < len(const_input_buffer):
                    del const_input_buffer[cursor_pos_in_buffer]
            elif const_key == term.KEY_LEFT:
                # Move cursor left
                if cursor_pos_in_buffer > 0:
                    cursor_pos_in_buffer -= 1
            elif const_key == term.KEY_RIGHT:
                # Move cursor right
                if cursor_pos_in_buffer < len(const_input_buffer):
                    cursor_pos_in_buffer += 1
            elif const_key.isprintable() and not const_key.is_sequence:
                # Add printable characters (and not special sequences) to the buffer
                # Insert at current cursor position
                const_input_buffer.insert(cursor_pos_in_buffer, str(const_key))
                cursor_pos_in_buffer += 1

    # After loop, clear the input line to leave a clean display
    print(term.move(const_start_row, const_start_col) + term.clear_eol, end="")
    # Return the collected string
    return "".join(const_input_buffer)

def render_char_at_position(
    term: Terminal,
    char_to_render: str,
    position: Tuple[int, int]
) -> None:
    """
    Renders a single character at the specified row and column using blessed.

    Args:
        term: The blessed Terminal instance.
        char_to_render: The character to print.
        position: A Coordinates NamedTuple with 'row' and 'column'.
    """
    # Ensure the character is indeed a single character to avoid unexpected behavior
    # For simplicity, we'll just take the first char if more are provided.
    const_char = char_to_render[0] if char_to_render else ' '

    # Move the cursor to the desired position and then print the character
    # The 'end=""' prevents a newline after printing the character.
    print(term.move(position[0], position[1]) + const_char, end="")

def render_box(term: Terminal, position: Tuple[int, int], box_content: str) -> None:
    """
    ------
    | xo |
    ------
    """
    first_line = term.move(position[0], position[1]) + "------"
    print(first_line)
    second_lint = term.move(position[0] + 1, position[1]) + "| " + box_content + " |"
    print(second_lint)
    third_line = term.move(position[0] + 2, position[1]) + "------"
    print(third_line)

def get_box_content(cell_value: int, placeholder: str) -> str:
    if cell_value == 1:
        return "x"
    elif cell_value == -1:
        return "o"
    return placeholder


def render_small_board(term: Terminal, position: Tuple[int, int], small_board: SmallBoard, board_number: int, isActive: bool):
    """
    1a 1b 1c
    1d 1e 1f
    1g 1h 1i
    """

    top = position[0]
    left = position[1]

    render_box(term, (top, left), get_box_content(small_board.squares[0], f"{board_number}a" if isActive else "  "))
    left += 6
    render_box(term, (top, left), get_box_content(small_board.squares[1], f"{board_number}b" if isActive else "  "))
    left += 6
    render_box(term, (top, left), get_box_content(small_board.squares[2], f"{board_number}c" if isActive else "  "))
    top += 3
    left = position[1]
    render_box(term, (top, left), get_box_content(small_board.squares[3], f"{board_number}d" if isActive else "  "))
    left += 6
    render_box(term, (top, left), get_box_content(small_board.squares[4], f"{board_number}e" if isActive else "  "))
    left += 6
    render_box(term, (top, left), get_box_content(small_board.squares[5], f"{board_number}f" if isActive else "  "))
    top += 3
    left = position[1]
    render_box(term, (top, left), get_box_content(small_board.squares[6], f"{board_number}g" if isActive else "  "))
    left += 6
    render_box(term, (top, left), get_box_content(small_board.squares[7], f"{board_number}h" if isActive else "  "))
    left += 6
    render_box(term, (top, left), get_box_content(small_board.squares[8], f"{board_number}i" if isActive else "  "))


def renderBoard(term: Terminal, board: Board, active_small_boards: List[int]):

        # Clear the entire screen initially
        print(term.home + term.clear)
        """
        18 wide
        9 tall
        """
        # render the first box
        render_small_board(term, (0, 0), board.small_boards[0], 1, 1 in active_small_boards)
        render_small_board(term, (0, 20), board.small_boards[1], 2, 2 in active_small_boards)
        render_small_board(term, (0, 40), board.small_boards[2], 3, 3 in active_small_boards)
        render_small_board(term, (10, 0), board.small_boards[3], 4, 4 in active_small_boards)
        render_small_board(term, (10, 20), board.small_boards[4], 5, 5 in active_small_boards)
        render_small_board(term, (10, 40), board.small_boards[5], 6, 6 in active_small_boards)
        render_small_board(term, (20, 0), board.small_boards[6], 7, 7 in active_small_boards)
        render_small_board(term, (20, 20), board.small_boards[7], 8, 8 in active_small_boards)
        render_small_board(term, (20, 40), board.small_boards[8], 9, 9 in active_small_boards)


        


def makeMove(board: Board, active_small_boards: List[int], move: str, is_first_user: bool) -> Tuple[Board, List[int]]:
    # make the move or fail bc invalid move
    new_board = board
    active_small_boards = []
    return new_board, active_small_boards

def checkSmallWin(small_board: SmallBoard):
    pass

def checkWin(board_position: Board):
    pass

def checkSmallDraw(small_board: SmallBoard):
    pass

def checkDraw(board_position: Board):
    pass

# game loop

board = Board(small_boards=[
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
    SmallBoard(squares=[0, 0, 0, 0, 0, 0, 0, 0, 0]),
])

def safe_int(s: str)-> int:
    try:
        return int(s)
    except ValueError:
        return -1


with term.fullscreen(), term.hidden_cursor():
    # first user move
    active_small_boards = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    renderBoard(term, board, active_small_boards)

    is_first_user = True

    while True:
        renderBoard(term, board, active_small_boards)
        valid_move = False
        new_board: Board | None = None
        move = blessed_input(term, "Enter the square where you want to move: ")
        if move == "exit":
                exit(0)
        if len(move) != 2:
            blessed_input(term, "Invalid move. Press enter to try again")
            continue

        move_board = move[0]
        move_position = move[1]

        if move_board not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"] or safe_int(move_board) not in active_small_boards or move_position not in ["a", "b", "c", "d", "e", "f", "g", "h", "i"]:
            blessed_input(term, "Invalid move. Press enter to try again")
            continue
        new_board, active_small_boards = makeMove(board, active_small_boards, move, is_first_user)

        print(term.move(term.height -3, 0) + str(active_small_boards))
        blessed_input(term, "Press enter to continue", position=(term.height - 2, 0))

        if not isinstance(new_board, Board) or not type(active_small_boards) == list:
            raise Exception("this should not happen")

        board = new_board

        won_by_player = checkWin(board)
        if won_by_player:
            print(f"player {won_by_player} won")
            break

        is_first_user = not is_first_user
        print("Player 1s turn" if is_first_user else "Player 2s turn")
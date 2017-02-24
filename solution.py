assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [s + t for s in A for t in B]


boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Adding this, will simply add the constraint similar to adding one more unit
# Diagnonal 1 as a constraint
diagonal_1 = [[rows[i]+cols[8 - i] for i in range(9)]]
# Diagnonal 2 as a constraint
diagonal_2 = [[rows[i]+cols[i] for i in range(9)]]

unitlist = row_units + column_units + square_units + diagonal_1 + diagonal_2
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for box in values:
        # Considering only twins, i.e. the ones with two possible values
        if len(values[box]) != 2:
            continue

        # For every peer for the given box
        for peer in peers[box]:
            # Taking only the one which has equivalent value
            if values[peer] != values[box]:
                continue
            # Taking all the common peers
            common_peers = peers[box] & peers[peer]
            # For all the common peers
            for common_peer in common_peers:
                # Just to make sure that no single valued field is made empty
                if len(values[common_peer]) < 2:
                    continue
                # Remove all of these pair values from the peers
                for c in values[box]:
                    values = assign_value(values, common_peer, values[common_peer].replace(c,''))
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    d = {}
    i = 0
    for r in rows:
        for c in cols:
            if grid[i] == '.':
                d[r+c] = '123456789'
            else:
                d[r+c] = grid[i]
            i += 1
    return d


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    # To make sure that every box is transformed only ones
    touched = dict((s, False) for s in boxes)
    for box in peers:
        # To make sure that no single valued box is made empty
        if not len(values[box]) > 1:
            continue
        for peer in peers[box]:
            # Make sure that only single valued box is used for elimintation
            if len(values[peer]) > 1 or touched[peer]:
                continue
            # Eliminate all the fixed values from peers
            if values[peer] in values[box]:
                values = assign_value(values, box, values[box].replace(values[peer], ''))
                touched[box] = True
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # TODO: Implement only choice strategy here
    for unit in unitlist:
        count = dict([(str(i), []) for i in range(1, 10)])
        for key in unit:
            if len(values[key]) == 0:
                continue
            for s in values[key]:
                count[s].append(key)
        for key in count:
            if len(count[key]) == 1:
                values = assign_value(values, count[key][0], key)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Naked Twins Strategy
        naked_twins(values.copy())

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return None
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if not values:
        return False ## Failed earlier

    solved = True
    for key in values:
        if len(values[key]) > 1:
            solved = False

    if solved:
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    min_count = 9
    min_key = 'A1'
    for key in values:
        if len(values[key]) > 1 and len(values[key]) < min_count:
            min_key = key
            min_count = len(values[min_key])
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not None), return that answer!
    for value in values[min_key]:
        values_ = values.copy()
        values_ = assign_value(values_, min_key, value)
        child = search(values_)
        if child:
            return child
        else:
            values_ = assign_value(values_, min_key, values[min_key])


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

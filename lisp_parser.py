#!/usr/bin/env python

import re

def parse_expression(expression):
    """parse a string representing a lisp expression into a syntax tree"""
    tokens = re.findall("\w+|[()+\-*/><=]", expression)
    return parse_tokens(tokens)
    
def parse_tokens(tokens):
    """parse tokens of a lisp expresson into a syntax tree"""
    token = tokens.pop(0)
    if token == '(':
        return parse_list(tokens)
    else:
        return typed(token)

def parse_list(tokens):
    """parse tokens of a lisp list expression"""
    lst = []
    while tokens[0] != ')':
        lst.append(parse_tokens(tokens))
    tokens.pop(0)
    return lst

def typed(token):
    """convert a token into a python type
       integer, float or string"""
    try:
        value = int(token)
        return value
    except ValueError:
        pass
    try:
        value = float(token)
        return value
    except ValueError:
        pass
    return token


class Environment(object):
    """environments store variable name value bindings in the form of a dictionary"""
    def __init__(self, var_names, values, parent_environment):
        self.parent_environment = parent_environment
        self.frame = dict(zip(var_names, values))

    def lookup(self, var_name):
        if var_name in self.frame:
            return self.frame[var_name]
        elif self.parent_environment:
            return self.parent_environment.lookup(var_name)
        else:
            raise Exception("%s is not defined" % (var_name))

    def set_var(self, var_name, value):
        self.frame[var_name] = value


class Procedure(object):
    """non-primitive user defined procedures"""
    def __init__(self, parameters, expression, environment):
        self.parameters = parameters
        self.expression = expression
        self.environment = environment

    def __call__(self, *args):
        # TODO rename frame?
        frame = Environment(self.parameters, args, self.environment)
        return evaluate(self.expression, frame)
        

def evaluate(exptree, environment):
    """evaluates an expression tree (syntax tree)"""
    # primitives
    if isinstance(exptree, str):
        return environment.lookup(exptree)
    elif isinstance(exptree, int) or isinstance(exptree, float):
        return exptree
    # special forms
    elif exptree[0] == 'def' or exptree[0] == 'define':
        var = exptree[1]
        val = evaluate(exptree[2], environment)
        environment.set_var(var, val)
    elif exptree[0] == 'if':
        predicate = exptree[1]
        true_clause = exptree[2]
        false_clause = exptree[3]
        if evaluate(predicate, environment):
            return evaluate(true_clause, environment)
        else:
            return evaluate(false_clause, environment)
    elif exptree[0] == 'fn' or exptree[0] == 'lambda':
        params = exptree[1]
        expression = exptree[2] # procedure body
        return Procedure(params, expression, environment)
    # procedures
    elif isinstance(exptree, list):
        func = evaluate(exptree[0], environment)
        args = [evaluate(arg, environment) for arg in exptree[1:]]
        return func(*args)
    else:
        raise SyntaxError("Unsupported Expression")


def init_default_environment():
    """initializes a default environment (dictionary) with some primitive procedures"""
    def add(*args):
        # alternative to reduce
        #if len(args) == 0:
            #return 0
        #return args[0] + add(*args[1:])
        return reduce(lambda x,y: x + y, args)

    def subtract(*args):
        return reduce(lambda x,y: x - y, args)

    def multiply(*args):
        return reduce(lambda x,y: x * y, args)

    def divide(*args):
        return reduce(lambda x,y: x / y, args)

    def first(args):
        return args[0]

    def rest(args):
        return args[1:]

    def create_list(*args):
        return list(args)

    def less_than(*args):
        # currently only binary less than
        # TODO: raise SyntaxError if number of args incorrect
        return args[0] < args[1]

    def greater_than(*args):
        # currently only binary greater than
        return args[0] > args[1]

    def equals(*args):
        # currently only binary equals 
        return args[0] == args[1]
    
    default_environment = Environment((), (), None)
    default_environment.set_var('+', add)
    default_environment.set_var('-', subtract)
    default_environment.set_var('*', multiply)
    default_environment.set_var('/', divide)
    default_environment.set_var('first', first)
    default_environment.set_var('rest', rest)
    default_environment.set_var('list', create_list)
    default_environment.set_var('true', True)
    default_environment.set_var('false', False)
    default_environment.set_var('<', less_than)
    default_environment.set_var('>', greater_than)
    default_environment.set_var('=', equals)

    return default_environment


def repl():
    """Runs a lisp repl"""
    environment = init_default_environment()
    while True:
        exp = raw_input("lisp> ")
        if exp == "quit":
            break
        exptree = parse_expression(exp)
        print evaluate(exptree, environment)


def test_parse():
    """Tests whether the parser generates the expected expression tree from a string expression"""
    # TODO: convert to nose test
    print "==== TESTING PARSE ===="
    exp_2_tree = { "(+ 2 3)": ['+', 2, 3],
                  "5": 5,
                  "(first (list 1 (+ 2 3) 9))": ['first', ['list', 1, ['+', 2, 3], 9]]}

    for exp, tree in exp_2_tree.items():
        print "expression        :", exp
        print "expected ast      :", tree
        print "parsed ast        :", parse_expression(exp)
        print "expected == parsed:", tree == parse_expression(exp)

        print "\n"


def test_evaluate():
    """Tests whether a string expression evaluates to an expected value"""
    # TODO: convert to nose test
    print "==== TESTING EVALUATE ===="
    environment = init_default_environment()
    exp_2_value = { "(+ 1 2 3)": 6,
                    "5": 5, 
                    "(list 1 2 3)": [1,2,3],
                    "(first (list 1 (+ 2 3) 9))": 1}
    for exp, val in exp_2_value.items():
        exptree = parse_expression(exp)
        evaluated = evaluate(exptree, environment)
        print "expression           :", exp
        print "expected value       :", val
        print "evaluated            :", evaluated 
        print "expected == evaluated:", val == evaluated
        print "\n"


if __name__ == '__main__':
    test_parse()
    test_evaluate()
    repl()

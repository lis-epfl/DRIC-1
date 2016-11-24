from re import compile

class RangeQuery(object):
    
    s_single_value_pattern = r'((end)|((\+|-)?\d+))'
    s_range_pattern = r'({}:{})'.format(s_single_value_pattern, s_single_value_pattern)
    s_range_step_pattern = r'({}:{}:{})'.format(s_single_value_pattern, s_single_value_pattern, s_single_value_pattern)
    s_single_query_pattern = r'({}|{}|{})'.format(s_single_value_pattern, s_range_pattern, s_range_step_pattern)

    single_value_pattern = compile(r'^{}$'.format(s_single_value_pattern))
    range_pattern = compile(r'^{}$'.format(s_range_pattern))
    range_step_pattern = compile(r'^{}$'.format(s_range_step_pattern))
    single_query_pattern = compile(r'^{}$'.format(s_single_query_pattern))
    query_pattern = compile(r'^({},)*{}$'.format(s_single_query_pattern, s_single_query_pattern))

    def __init__(self, query, end=None):
        if not self.query_pattern.match(query):
            raise ValueError('Query must match pattern {}'.format(self.query_pattern.pattern))

        if query.find('end') >= 0:
            if end is None:
                raise ValueError('Query cannot contains the \'end\' keyword if no end value has been specified')
            query = query.replace('end', str(end))
        self.tokens = query.split(',')

    def __iter__(self):
        for token in self.tokens:
            gen = None
            if self.single_value_pattern.match(token):
                gen = SingleValueGenerator(token)
            elif self.range_pattern.match(token):
                gen = RangeGenerator(token)
            elif self.range_step_pattern.match(token):
                gen = RangeStepGenerator(token)
            else:
                raise ValueError('Unparsable token "{}"'.format(token))
            if gen is not None:
                for v in gen:
                    yield v
            

class SingleValueGenerator(object):
    def __init__(self, token):
        self.value = int(token)
        
    def __iter__(self):
        yield self.value

class RangeGenerator(object):
    def __init__(self, token):
        subtokens = token.split(':')
        self.start = int(subtokens[0])
        self.stop  = int(subtokens[1])
        if self.start < self.stop:
            step = 1 
        elif self.start > self.stop:
            step = -1
        else:
            step = 0
        new_token = token.replace(':', ':{}:'.format(step))
        self.subgenerator = RangeStepGenerator(new_token)
        
    def __iter__(self):
        for v in self.subgenerator:
            yield v

class RangeStepGenerator(object):
    def __init__(self, token):
        subtokens = token.split(':')
        self.start = int(subtokens[0])
        self.step  = int(subtokens[1])
        self.stop  = int(subtokens[2])

    def __iter__(self):
        # can we make this code tastier ? 
        if self.step > 0:
            i = self.start
            while i <= self.stop:
                yield i
                i = i + self.step
        elif self.step < 0:
            i = self.start
            while i >= self.stop:
                yield i
                i = i + self.step

if __name__ == '__main__':
    # TODO unit testing
    query = '2:2:6'
    print(query)
    expected = [2, 4, 6]
    result = list(RangeQuery(query))
    print('{} {} {} {}'.format(bool(expected == result), query, expected, result))

    query = '10:-2:5'
    print(query)
    expected = [10, 8, 6]
    result = list(RangeQuery(query))
    print('{} {} {} {}'.format(bool(expected == result), query, expected, result))

    query = '2,86'
    print(query)
    expected = [2, 86]
    result = list(RangeQuery(query, 10))
    print('{} {} {} {}'.format(bool(expected == result), query, expected, result))

    query = '-2,+86'
    print(query)
    expected = [-2, 86]
    result = list(RangeQuery(query, 10))
    print('{} {} {} {}'.format(bool(expected == result), query, expected, result))

    query = '1:4,4:1'
    print(query)
    expected = [1,2,3,4,4,3,2,1]
    result = list(RangeQuery(query, 10))
    print('{} {} {} {}'.format(bool(expected == result), query, expected, result))

    query = 'end:-2:5'
    print(query)
    expected = [10, 8, 6]
    result = list(RangeQuery(query, 10))
    print('{} {} {} {}'.format(bool(expected == result), query, expected, result))

from zope.interface import Interface, implements

from twisted.python.components import globalRegistry

class IRuleFact(Interface):
    def rule():
        pass

class Monster(object):
    implements(IRuleFact)
    def rule(self):
        print "%s is monstrous" % (self,)

class IPublisher(Interface):
    def publish():
        pass

class PublishMonsterLatex(object):
    __used_for__ = (IRuleFact,)
    implements(IPublisher)

    def __init__(self, x):
        self.x = x

    def publish(self):
        print "(1)publish latex %s" % (self.x,)

class PublishMonsterHTML(object):
    __used_for__ = (IRuleFact,)
    implements(IPublisher)

    def __init__(self, x):
        self.x = x

    def publish(self):
        print "(2)publish html %s" % (self.x,)

class PublishFeatLatex(object):
    __used_for__ = (IRuleFact,)
    implements(IPublisher)

    def __init__(self, x):
        self.x = x

    def publish(self):
        print "(2)publish html %s" % (self.x,)

class PublishSkillLatex(object):
    __used_for__ = (IRuleFact,)
    implements(IPublisher)

    def __init__(self, x):
        self.x = x

    def publish(self):
        print "(2)publish html %s" % (self.x,)

class PublishFeatHTML(object):
    __used_for__ = (IRuleFact,)
    implements(IPublisher)

    def __init__(self, x):
        self.x = x

    def publish(self):
        print "(2)publish html %s" % (self.x,)

class PublishSkillHTML(object):
    __used_for__ = (IRuleFact,)
    implements(IPublisher)

    def __init__(self, x):
        self.x = x

    def publish(self):
        print "(2)publish html %s" % (self.x,)

class Feat(object):
    implements(IRuleFact)
    def rule(self):
        "%s is featitudinous" % (self,)

class Skill(object):
    implements(IRuleFact)
    def rule(self):
        "%s is skillful" % (self,)

def singleAdaptWithNameTuple():
    globalRegistry.register([IRuleFact], IPublisher, ('html', Monster), PublishMonsterHTML)
    globalRegistry.register([IRuleFact], IPublisher, ('latex', Monster), PublishMonsterLatex)
    globalRegistry.register([IRuleFact], IPublisher, ('html', Feat), PublishFeatHTML)
    globalRegistry.register([IRuleFact], IPublisher, ('latex', Feat), PublishFeatLatex)
    globalRegistry.register([IRuleFact], IPublisher, ('html', Skill),  PublishSkillHTML)
    globalRegistry.register([IRuleFact], IPublisher, ('latex', Skill), PublishSkillLatex)

    print globalRegistry.lookup([IRuleFact], IPublisher, ('html', Monster))
    print globalRegistry.lookup([IRuleFact], IPublisher, 'latex')
    print globalRegistry.lookup([IRuleFact], IPublisher, 'html')
    print globalRegistry.lookup([IRuleFact], IPublisher, 'latex')
    print globalRegistry.lookup([IRuleFact], IPublisher, 'html')
    print globalRegistry.lookup([IRuleFact], IPublisher, 'latex')


def singleAdaptWithClassFirst():
    globalRegistry.register([Monster], IPublisher, 'html', PublishMonsterHTML)
    globalRegistry.register([Monster], IPublisher, 'latex', PublishMonsterLatex)
    globalRegistry.register([Feat], IPublisher, 'html', PublishFeatHTML)
    globalRegistry.register([Feat], IPublisher, 'latex', PublishFeatLatex)
    globalRegistry.register([Skill], IPublisher, 'html',  PublishSkillHTML)
    globalRegistry.register([Skill], IPublisher, 'latex', PublishSkillLatex)

    print globalRegistry.lookup([Monster()], IPublisher, 'html')
    print globalRegistry.lookup([Monster()], IPublisher, 'latex')
    print globalRegistry.lookup([Feat()], IPublisher, 'html')
    print globalRegistry.lookup([Skill()], IPublisher, 'html')
    print globalRegistry.lookup([Skill()], IPublisher, 'latex')


# fails:
singleAdaptWithNameTuple()
# fails:
singleAdaptWithClassFirst()

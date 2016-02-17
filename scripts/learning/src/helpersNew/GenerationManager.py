# TODO check that both of these imports are needed
from collections import OrderedDict
import collections
import copy
import random
from helpersNew import dictTools

#
# THIS WILL LIKELY BE CHANGED TO A LIST INSTEAD OF A DICT
# WHEN VALUES ARE CALCULATED DYNAMICALLY, NO NEED FOR DICT
# TREATED AS LIST UNTIL CLARIFIED
#

class LearningDictionary(collections.OrderedDict):
    """
    Dictionary for storing entities for learning trials.
    Dynamically calculates all accessible properties.
    """

    def __init__(self, ID):
        """
        Constructor for a LearningDictionary.
        Requires an ID to reference the dictionary.
        """
        # Create internal variables for dynamic calculation
        self.ID = ID
        self._maxScoreUpdated = False
        self._maxScore = 0
        self._minScoreUpdated = False
        self._minScore = 0
        self._avgScoreUpdated = False
        self._avgScore = 0
        self._totalScoreUpdated = False
        self._totalScore = 0


        collections.OrderedDict.__init__(self)
    
    def __setitem__(self, key, value):
        """
        If the domain element already appears in the dictionary, delete it.
        Add the given pair as the last element in the dictionary.
        Calculates dynamically.
        
        key -- Another LearningDictionary.
        value -- Fitness score of the LearningDictionary's elements.
        """
        if key in self:
            del self[key]
        # Although the same domain element is added, the range element could be different.
        # Thus, the average and max scores could change.
        self._needsUpdate()
        collections.OrderedDict.__setitem__(self, key, value)

    def _needsUpdate(self):
        """
        Flags all calculated values as requiring updating.
        """
        self._maxScoreUpdated = False
        self._avgScoreUpdated = False
        self._minScoreUpdated = False

    def getAvgScore(self):
        """
        Returns the average score of the elements in the dictionary.
        Calculates dynamically.
        """
        sum   = 0
        count = 0
        if not self._avgScoreUpdated:
            for value in collections.OrderedDict.itervalues(self):
                sum   += value
                count += 1    
            self._avgScore = sum / count
            self._avgScoreUpdated = True
        return self._avgScore

    def getMaxScore(self):
        """
        Returns the maximum score of the elements in the dictionary.
        Calculates dynamically.
        """
        if not self._maxScoreUpdated:
            for value in collections.OrderedDict.itervalues(self):
                self._maxScore = max(self._maxScore, value)
            self._maxScoreUpdated = True
        return self._maxScore

    def getMinScore(self):
        """
        Returns the minimum of the value elements in the dictionary.
        Calculates dynamically.
        """
        if not self._minScoreUpdated:
            for value in collections.OrderedDict.itervalues(self):
                self._minScore = min(self._minScore, value)
            self._minScoreUpdated = True
        return self._minScore

    def getTotalScore(self):
        """
        Returns the sum of the value elements in the dictionary.
        Calculates dynamically.
        """
        if not self._totalScoreUpdated:
            self._totalScore = 0
            for value in collections.OrderedDict.itervalues(self):
                self._totalScore = self._totalScore + value
            self._totalScoreUpdated = True
        return self._totalScore

class Generation:

    def __init__(self, generationID, membersParam=None):
        self.generationID = generationID
        self._nextMemberID = 0
        
        # Create internal variables for dynamic calculation
        self._totalScoreUpdated = False
        self._totalScore = 0

        self._sorted = False
        self._componentPopulations = {}

        # Member dictionary
        self._members = []

        if membersParam:
            for member in membersParam:
                self._members.append(member)

    def getID(self):
        return self.generationID

    def getComponentPopulation(self, componentName):
        return copy.deepcopy(self._componentPopulations[componentName])

    def getComponentPopulations(self):
        return copy.deepcopy(self._componentPopulations)

    def addComponentPopulation(self, componentName, componentPopulation):
        for component in componentPopulation:
            self.addComponentMember(componentName, component)

    def generateMemberFromComponents(self):
        memberID = self._getNextMemberID()
        newMember = Member(memberID=memberID,
                           generationID=self.generationID)

        for componentName, componentPopulation in self._componentPopulations.iteritems():
            newMember.components[componentName] = copy.deepcopy(random.choice(componentPopulation))
        self.addMember(newMember)
        return newMember

    def addComponentMember(self, componentName, component):
        localComponent = copy.deepcopy(component)
        localComponent["generationID"] = self.generationID
        if not componentName in self._componentPopulations:
            self._componentPopulations[componentName] = []
        self._componentPopulations[componentName].append(localComponent)

    def _getNextMemberID(self):
        memberID = self._nextMemberID
        self._nextMemberID += 1
        return memberID

    def getComponentNames(self):
        return self._componentPopulations.keys()

    def addMember(self, member):
        self._totalScoreUpdated = False
        self._sorted = False
        self._members.append(member)

    def getMember(self, ID):
        return self._members[ID]

    # Not sure if this is a deep copy or not
    def getMembers(self):
        return list(self._members)

    def getTotalScore(self):
        """
        Returns the sum of the value elements in the dictionary.
        Calculates dynamically.
        """
        if not self._totalScoreUpdated:
            self._totalScore = 0
            for member in self._members:
                self._totalScore += member.getScore()
            self._totalScoreUpdated = True
        return self._totalScore

    # O(N^2), can be O(Nlog(N))
    # Higher complexity for simpler code
    def sortMembers(self):
        """
        Sorts the members of the dictionary.
        Calculates dynamically.
        """
        if not self._sorted:
            newList = [self._members[0]]
            members = list(self._members)
            for item in range(len(self._members)):
                maxIndex = self._maxMemberIndex(members)
                maxElement = members.pop(maxIndex)
                newList.append(maxElement)
            self._members = newList
            self._sorted = True

    # O(N)
    # Not calculated dynamically because members argument may not be self._members
    def _maxMemberIndex(self, members):
        max = members[0].getScore()
        maxIndex = 0
        index = 0
        for member in members[1:]:
            score = member.getScore()
            index += 1
            if score > max:
                max = score
                index = maxIndex
        if max == 0:
            raise Exception("Only negative scores in generation. Is this really an error?")
        return maxIndex

class Member(object):
    """
    Dictionary for storing entities for learning trials.
    Dynamically calculates all accessible properties.

    TODO:
    Create a copy() function.
    """

    def __init__(self, memberID=-1, generationID=-1, components=None, seedMember=None):
        self.filePath = None
        if seedMember:
            self._score = seedMember._score
            self._trials = seedMember._trials
            self.components = seedMember.components
        else:
            self.memberID = memberID
            if not components:
                self.components = {}
            else:
                self.components = components
            self._trials = []
            self._score = None

        if not "memberID" in self.components:
            assert type(generationID) == type(1)
            print "Setting memberID to: " + str(memberID)
            self.components['memberID'] = memberID
        if not "generationID" in self.components:
            assert type(generationID) == type(1)
            print "Setting generationID to: " + str(generationID)
            self.components['generationID'] = generationID

    # Score encapsulated to indicate that it should not be altered by user
    def getScore(self):
        if not self._score:
            raise Exception("getScore called when score has not yet been assigned.")
        else:
            return self._score

    def copy(self):
        return Member(-1,self.parameters.copy())

    def _setScore(self, scoreMethod, trials):
        self._trials = trials

        # Scoring by average
        if scoreMethod == "average":
            sum = 0
            count = 0
            for trial in self._trials:
                sum += trial['score']
                count += 1
            self._score = sum / count

        # Scoring by maximum
        elif scoreMethod == "max":
            for trial in self._trials:
                self._score = max(self._score, trial['score'])

        # Raise exception on unknown scoring method
        else:
            raise Exception("MEMBER: <TODO>: Exception Hierarchy.")

# In the process of removing calls to subclasses of Member.
# Replacing them all with just "Member"
# TODO: Refactored out in favor of Member
class Controller(Member):

    # DEFAULTS = {
    #     'nodeVals' : {
    #         'Min' : 0,
    #         'Max' : 1
    #         },
    #     'edgeVals' : {
    #         'Min' : 0,
    #         'Max' : 1
    #         },
    #     'feedbackVals' : {
    #         'Min'  : -1,
    #         'Max'  : 1
    #         },
    #     'goalVals' : {
    #         'Min' : -1,
    #         'Max' : 1
    #         }
    #     }

    def __init__(self, memberID=-1, generationID=-1, seedMember=None):
        assert type(generationID) == type(1)
        if seedMember:
            self._score = seedMember._score
            self._trials = seedMember._trials
            self.components = seedMember.components
        else:
            # This is necessary because calling the super constructor returns a pointer to the same instance
            # Why? Unknown. Investigating.
            self.memberID = memberID
            self.components = {}
            self._trials = []
            self._score = None

        if not "memberID" in self.components:
            print "Setting memberID to: " + str(memberID)
            self.components['memberID'] = memberID
        if not "generationID" in self.components:
            assert type(generationID) == type(1)
            print "Setting generationID to: " + str(generationID)
            self.components['generationID'] = generationID

class Model(Member):
    ""
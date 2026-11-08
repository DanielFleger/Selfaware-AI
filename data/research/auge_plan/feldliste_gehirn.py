"""Feldliste fuers Gehirn (B-168): jedes nutzbare Feld bekommt einen Bedarf.

Eingabe:  sichtschranke.csv, zustand_felder.csv, nie_gesehen_lauf_f_und_k.csv
Ausgabe:  feldliste_gehirn.csv, Feldliste_Gehirn.md
Lauf aus dem Repo-Stamm, erst sichtschranke.py (nimmt ki, zufall und unklar von hier), dann dieses Skript:
    python data/research/auge_plan/sichtschranke.py
    python data/research/auge_plan/feldliste_gehirn.py

Bedarf:   takt      jeden Takt: aendert sich im Kampf und zaehlt fuer Entscheidungen
          selten    bei Aenderung oder alle paar Takte: Wirtschaft, Bauten, Gruppen, Karte
          einmal    beim Entstehen des Objekts oder zum Partiestart: Art, Ort eines Gebaeudes, Regeln
          entbehrlich  nur Bild, Hilfswert der Engine oder aus anderen Feldern ableitbar
          ki        Innenleben der Gegner-KI: fuers Gehirn gesperrt (FAIRNESS R3/F5)
          zufall    Zufallswert: fuers Gehirn gesperrt (FAIRNESS F1)
          unklar    Name sagt nicht, was es ist: ungenutzt, bis geklaert

Die Einordnung steht bewusst als vollstaendige Namensliste hier und nicht als Muster: Feld fuer Feld nachpruefbar. Das
Skript bricht ab, wenn ein Feld fehlt oder ein Name nicht vorkommt. Quelle "name_unklar": von der Sichtschranke nur wegen
ihres Namens als "unbekannt" gefuehrt, die Bedeutung ist aber aus dem Namen und den schreibenden Funktionen erkennbar.
"""

import collections
import csv
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
csv.field_size_limit(10**7)


def w(text):
    return text.split()


def reihe(stamm, von, bis):
    return [f"{stamm}{i}" for i in range(von, bis + 1)]


# (Bereich, Vorsatz) -> Bedarf -> Namen. Vorsatz gilt fuer die Namen der Zeile, "" = Name steht so in der Liste.
E_ = "units[]."
G_ = "buildings[]."
T_ = "tribes[]."
Q_ = "entityArray[]."
M_ = "mapAndTime."
P_ = "playerDataArray[]."
GRUPPEN = {
    "DAT_UnitsState": [
        (E_, "takt", w("""x y microXPosition microYPosition tile health state substate logicalState dying
            destinationNeeded destinationXPosition destinationYPosition destinationTilePosition plannedDestinationX plannedDestinationY
            currentIndexInPathPlan totalSizeOfPathPlan targetingType target targetX targetY targetUID targetedBuildingTile
            attackAtTileX attackAtTileY shootTargetMicroX shootTargetMicroY shootTargetZ shootTargetedUnit attackedUnitID
            attackedBy closestEnemyMicroDistance tribeID calculatedMovementSpeed animationFrame animationCycleNumber
            climbingState terrainOrClimbHeight buildingHeight""")),
        (E_, "selten", w("""tribeUID idInTribe lookForEnemy lastEncounteredEnemyPlayerID goToRallyPoint movementSpeed
            isMatchingSpeed banked blessedAmount seated idle working workplaceBuildingID_1 workplaceBuildingUID
            workplaceBuildingTilePosition buildingID workerIndex resourceToDeposit resourcesGatheredCount productivityDiv100
            productivityMod100 woodcutterTreeUID traderHorsesTrader poleturner_spearOrPike stoneAmmunition shootBeforeStop
            nextAttackHurtsWall digTileTarget ladderExitXPosition ladderExitYPosition cannotClimb wallDataID
            distanceToEnemyUnitLadders rallyRelatedFlag selectionTargetUnitID engineerManningSiegeStateRef_checkType
            manningEngineerRef[] manningEngineerUIDRef tunnelerFinishedDigging huntedBy pathPlanStart[] targetX_2 targetY_2
            unitTypeToChangeInto unitType_3 state_2 workRelatedA workRelatedB workRelatedC workTimer
            usingTeleport moveRelatedFlag disappearFadeAlphaCountdown""")),
        ("", "selten", w("DAT_EuroUnitAcquisitionFailReason DAT_EuroUnitRequiredResource")),
        (E_, "einmal", w("uid unitType owner maxHealth maxHealthRatingLord time unitCanClimb horseArcherShootCheckInterval")),
        (E_, "entbehrlich", w("""animationCycleNumberHasJustIncremented animationLeapTicksTotal animationSheetFrameOffset
            animationSpeed animationTicker assassinHeightDifference calculatedOwnerPlayerIndex cachedState climbDataID
            climbDataRelated climbDirection climbingDirection counter displayColorPlayerID
            drawXOffset drawYOffset facingDirection facingDirectionMapOrientationCorrected fadeCounter fadeType firstNameIndex
            gfxNumber graphicSize healthPercentage healthbar heightDiv10 horseArcherShootingVariation imageID2 isSelected
            jugglerCount mimicCurrentXPosition mimicCurrentYPosition moveDelay moveInstructionSpeedDelayTracker
            movementDistance movementRelated movementRunUpTime negativeHeight orientationRelatedPositionX
            orientationRelatedPositionY ownerOfAssassinScaledObject previousTilePosition someDrawYOffset spriteID state.generic
            stateBasedSpeed state_3 topSpeedDelayIndex tunnelerFrame updateTickTracker vanish wasOnStoneGate
            drawHeight1 drawWidth drawX drawY""")),
        ("", "entbehrlich", w("DAT_LastSelectedUnitID")),
        (E_, "ki", w("aiUnitBehaviourType siegeTargetPlayerID")),
        (E_, "unklar", w("""_someX_2 _someY_2 field_0x30_animRelated field_0x3c3 field_0x40d field_0x40e field_0x40f field_0x411
            field_0x83 someMatchTimeVariable someUnitStat4 targetShootRelated unkAttackRelated unkLadderClimbRelated""")),
    ],
    "DAT_BuildingsState": [
        (G_, "takt", w("logicalState currentHealth fireDuration gateState")),
        (G_, "selten", w("""state hasUnitsOntop buildingProgress currentEmployeeCount currentlyNeededEmployeeCount gateState2
            drawbridgeState2 drawBridgeState1 gateCloseOpenTimer cooldownTimer containsSiegeMangonel1OrBallista2
            currentLimitOfResource currentNumberOfResource currentStoredResourceType flagonsOfAleOrCheeseOrReleaseDogs
            resourceAle resourceApple resourceArray_resourceTypePlus1[] resourceBow resourceBread resourceCheese
            resourceCrossbow resourceFlour resourceGold resourceHops resourceIron resourceIronArmor resourceLeatherArmor
            resourceMace resourceMeat resourcePartialPitch resourcePartialStone resourcePike resourcePitch
            resourceRelatedCountDown resourceSpear resourceStone resourceSword resourceWheat resourceWood
            numberOfAnimals growCounter wheatGrowStateRelated sleeping producedItemType producedItemTypeNext recruitTimer
            timeAlive ifFireThenResponsiblePlayer insideUnitID1 insideUnitID2 insideUnitID3 insideUnitID4 insideUnitUID1
            insideUnitUID2 insideUnitUID3 insideUnitUID4 unitID unitRefID unitRefUID workerID[] workerUID[] workers[]
            killingPitField laddermanDataID tribeID tribeUID oxTetherRelatedUnitID oxTetherRelatedUnitUID
            oxtetherLinkedQuarryID quarryLinkedOxTethers[] quarryStockpileID tunnelerCounter campgroundVclock""")),
        (G_, "einmal", w("""buildingType uid uidWhenPlaced x y xPosition yPosition microX microY owner maxHealth widthOrHeight
            buildingEntryX buildingEntryY currentTilePositionAdjusted orientation numberOfPopulationProvided
            buildingTypeBasedEmployeeCount buildMonthOrBuildOrder statueCommemoratingPlayerID""") + reihe("tileRef", 1, 36)),
        (G_, "entbehrlich", w("""animAdvanceThrottle animStateCounter animStateCounterTracker animationActive animationFrame
            animationIncrement animationIndex buildingIsVisuallyActive buildingVariation displayOwnerFlag
            entranceAttemptTileIndex ffBuildingVariation gfxOffset gfxOffset2 gfxOffset3 hovelVisualStyle noRubble
            oldVisualActiveState ownerFlagFrame pathLinkageRelated1 pathLinkageRelated2 renderAnimation shouldRenderRoof
            shouldRenderSomeOverlay someResourceNumber spriteID spriteID2 spriteOffetX spriteOffetY spriteSheetID
            tickRelatedVisuallyActiveIndicator visuallyActiveSpriteID miscDisplayLayerTile""")),
        ("", "entbehrlich", w("""campfireSpotOrientation campfireSpotX campfireSpotY counter farmerDestinationTile
            hopFarmerDestinationOffsetX hopFarmerDestinationOffsetY unitID""")),
        (G_, "ki", w("attackWave")),
        (G_, "zufall", w("fireRelatedRNG1")),
        (G_, "unklar", w("flag1 flag2 field_0x2a5 field_0x314 someX someY someUID")),
        ("", "unklar", w("siegeEngineCreationRelated01")),
    ],
    "DAT_TribesState": [
        (T_, "takt", w("targetX targetY tribeState targetBuildingID targetBuildingUID")),
        (T_, "selten", w("""size unitStance currentRallyPointIndex rallyPointArray[] rallyPointArray[][] rallyPointCount
            movementSpeed minimumMovementSpeed maximumMovementSpeed freeUnitSpeeds orientation facingDirection_1
            facingDirection_2 facingDirection_3 selectionTargetUnitID someUnitArrayIndex someUnitArray[] someUnitUIDArray[]
            unitsHealthPercentage""")),
        (T_, "einmal", w("uid uid2 tribeID tribeType tribeSubtype1 unitType owner unkIsAnimalTribe")),
        (T_, "ki", w("""attackWave attackInfo_someCounter1 archerRelated archerRelated2 siegeIndexValue1 siegeIndexValue2
            supportPointIndex oldSupportPointIndex targetPlayer_outpost tribeBehaviorType""")),
        (T_, "entbehrlich", w("countdown countdown2 counter time percentageSomething")),
        (T_, "unklar", w("someCounter1 someTile someTile2 someUnitID someUnitUID")),
        ("", "entbehrlich", w("""ALG_ResultTileIndex ALG_ResultX ALG_ResultY clans someUnitIDArrayCount
            someUnitIDMovementDistancePair[].movementDistance someUnitIDMovementDistancePair[].unitID""")),
    ],
    "DAT_EntityState": [
        (Q_, "takt", w("entityType logicalState owner xPosition yPosition microX microY tile height vCos vSin orientation "
                       "travelledDistance fireIntensity")),
        (Q_, "einmal", w("uid startingAngle startingHeight startingHeight_2 heightDifference height_2 x_2 y_2")),
        ("", "selten", w("fireCount")),
        (Q_, "entbehrlich", w("""_elapsedTimeOrGravityAccumulator graphicType2 graphicType2RelatedOffset imageID originX originY
            someMicroX someMicroY x1 y1 entityType2 fireParameter_0xb6 unitID uidRef unitUID unitID_healer""")),
        ("seagullArray[].", "entbehrlich", w("angle angle_2 someAngle x x_2 x_3 y y_2 y_3")),
    ],
    "DAT_TileMapState": [
        ("", "selten", w("""BuildingLayer[] BuildingWasLayer[] CertainPathLayer[] DamageLayer[] HeightLayer[] Logic2Layer[]
            LogicLayer[] OccupancyLayer[] OrganismLayer[] PathConnectionLayer[] PathLinkageLayer[] UnitLayer[] WalkLayer[]
            WallOwnerLayer[] currentMoatCount moatTileCount moats[].fillProgress moats[].owner moats[].someCountDown
            moats[].stage moats[].zeroOrTwo pitchDitches[].owner pitchDitches[].state""")),
        ("", "einmal", w("""DefaultHeightLayer[] mapSize mapOrientation rockOrientation maxPitchDitchCount moats[].tile moats[].x
            moats[].y pitchDitches[].tile pitchDitches[].uid pitchDitches[].x pitchDitches[].y""")),
        ("", "entbehrlich", w("""EntityLayer[] EntityLayerLT25[] ALG_MoatXResult ALG_MoatYResult DAT_CardinalTilesAroundTile
            DAT_SomeTile DAT_SomeX DAT_SomeY DAT_TempBuildingRotation buildingHeightLimit buildingMaxHeight
            buildingMaxHeightDifference buildingMinHeight buildingPlacementFail buildingPlacementFailReason
            buildingPlacementProperty_3 buildingPlacementProperty_4 buildingPlacementProperty_5 buildingPlacementProperty_6
            buildingPlacementProperty_7 buildingRotationRelatedValue buildingX buildingY constructionTileCount counter1
            currentMapperCommand directionTranslationMatrix[] heightBasedScreenYOffset[] illegalBuild placedBuildingID
            placementWarning someMoatTile wallPlacementCost DAT_WallTileCountCurrentDrag""")),
    ],
    "GameState.mapAndTime": [
        (M_, "selten", w("""armySizeLimit dayTicks deerCount gameOver gameOverTime month monthTicks playerIsAlive[]
            playerPopulationStatistics[] playerTeams[] week weekTicks year""")),
        (M_, "einmal", w("""buyAndSalesPriceArray[].buyPrice buyAndSalesPriceArray[].salesPrice difficulty euroRecruitable[]
            isResourceTradeable[] mercRecruitable[] noCowThrowing noDogs playerGroupArray[] rawDeerCount skirmishFogOfWar
            startGoods[] startingPopularity startingTroops[] strongWalls2 totalNoRushTicks singlePlayerHasKeepAndGranary""")),
        (M_, "entbehrlich", w("""cathedralRelated1 copyOfBuyAndSalesPrice[].buyPrice copyOfBuyAndSalesPrice[].salesPrice
            euroRecruitableCopy_index_0 euroRecruitableCopy_index_1_a euroRecruitableCopy_index_1_b euroRecruitableCopy_index_2
            euroRecruitableCopy_index_3_a_and_6_b euroRecruitableCopy_index_3_b euroRecruitableCopy_index_6_a
            euroRecruitableCopy_index_6_c monthChanged monthCopy startOfDay weekChanged yearChanged yearCopy""")),
    ],
    "DAT_GameSynchronyState": [
        ("", "selten", w("""DAT_ChatEventArray[].flag DAT_ChatEventArray[].objectPlayer DAT_ChatEventArray[].subjectPlayer
            DAT_ChatEventArray[].time DAT_ChatMessageArrayIndex DAT_ChatMessageArray[] DAT_ChatMessageObjectPlayerNameArray[]
            DAT_ChatMessageSubjectPlayerNameArray[] receivedChatMessage[] finalResults.finalBuidingsDestroyed[]
            finalResults.finalBuildingsBurned[] finalResults.finalBuildingsDestroyedWeighted[]
            finalResults.finalDateOfDeathInMonths[] finalResults.finalFoodProduced[] finalResults.finalGold[]
            finalResults.finalGoodsRecieved[] finalResults.finalGoodsSent[] finalResults.finalIronProduced[]
            finalResults.finalKillMatrix[] finalResults.finalKilledLords[] finalResults.finalMaxBadThings[]
            finalResults.finalMaxGoodThings[] finalResults.finalMaxPopulation[] finalResults.finalPitchProduced[]
            finalResults.finalStoneProduced[] finalResults.finalTimeAlive[] finalResults.finalTroopsKilledWeighted[]
            finalResults.finalTroopsProduced[] finalResults.finalWeaponsProduced[] finalResults.finalWoodProduced[]
            finalResults.monthEnd finalResults.yearEnd""")),
        ("", "einmal", w("""DAT_ChatMessageReceiverArray[] DAT_PlayerGroupArray[] DAT_PlayerNames[] DAT_PlayerNames[][]
            currentAIArray[] currentPlayerFullIDArray[] finalResults.active[] finalResults.monthStart finalResults.names[]
            finalResults.yearStart""")),
        ("", "entbehrlich", w("DAT_PlayerMatchTimes[] finalResults.padding1 finalResults.padding2[] finalResults.padding3[]")),
    ],
    "DAT_LandscapeState": [
        ("rocks[].", "einmal", w("orientation size tile type uid x y")),
        ("rocks[].", "entbehrlich", w("gfx one")),
        ("trees[].", "einmal", w("appleFarmID appleFarmUID microX microY size tile treeType treeTypeBasedValue1 treeTypeRelated2 "
                                 "uid xPosition yPosition")),
        ("trees[].", "selten", w("igniterPlayer stage state")),
        ("trees[].", "entbehrlich", w("""animationFrameIndex appleTreeColorVariation flag gmOriginX gmOriginY one stageRelated1
            stageRelated2 stageRelated4 stageTracker treeAdultHoodStageRelatedVisual3 zero zeroUpTo2""")),
        ("trees[].", "unklar", w("param_6")),
        ("", "selten", w("DAT_TotalOrganisms")),
        ("", "entbehrlich", w("maxTreeCount x y")),
    ],
    "DAT_WildlifeState": [
        ("", "entbehrlich", w("DAT_X10_Array_Section1034[] DAT_Y10_Array_Section1034[] candidateIndex candidateIndex2 casDisRelated")),
        ("grid[].", "entbehrlich", w("""camelCount casDisRelated2 castlebuildings chimps deerCount firstMember keeps lionCount
            rabbitCount separateAreaID trees unclaimedArea unitCount""")),
        ("grid[][].", "entbehrlich", w("""camelCount casDisRelated2 castlebuildings chimps deerCount keeps lionCount rabbitCount
            separateAreaID trees unclaimedArea unitCount""")),
    ],
    "DAT_MapPropertiesState": [
        ("", "einmal", w("""SEC_BowProducible_save SEC_MaceProducible_save SEC_MercRecruitable[] SEC_PikeProducible_save
            SEC_Section1065.tradeabilityArray[] SEC_Section1067.tunnelersCount SEC_SiegeInformation.archers
            SEC_SpearProducible_save SEC_StartingMonth SEC_StartingPopularity SEC_StartingResources[] SEC_StartingYear
            SEC_SwordProducible_save SEC_XbowProducible_save barracksRecruitability buildingAvailabilityRelatedFlags[]
            buildingAvailability[]""")),
        ("", "unklar", w("SEC_Section1080 SEC_Section1081 SEC_Section1089[] SEC_Section1090")),
    ],
    "DAT_WallAndPitchState": [
        ("", "entbehrlich", w("""countdown counter flag id index state uid wallPlacementInfoArray[].damage
            wallPlacementInfoArray[].height wallPlacementInfoArray[].logic""")),
    ],
    "DAT_GameState": [
        (P_, "selten", w("partialWoodCounter releaseDogsFlag timeTaxesOrRationsChange")),
    ],
    "GameState.playerDataArray": [
        (P_, "takt", w("closestEnemyDistanceToTheLord")),
        (P_, "selten", w("""aleRate appleCount areCarnivalUnitsPresent armySize availableHorses availablePeasantsAtFire
            availablePeasantsOrHousedPeasants badStuffCount beerPercentage beforeLastMonthsGold blessedPeoplePercentage
            breadCount cheeseCount chickenCount2 countArabSwordsman countArabianArcher countArabianArchersRelated
            countArmorersAndBlacksmiths countAssassins countAssassinsAndArabianSwordsman countBakers countBrewers
            countEconomyBuilding_fixme countEntities countFarms countFireThrowers countFirethrowers countFletchersPoleturners
            countHorseArchers countInns countIronMines countPitchRigs countRelatedToHorseArchers countSlaves countSlaves2
            countSlingers countSlingers2 countStoneQuarries countWoodcutters crowding currentArchers currentCrossbowmen
            currentEngineers currentKnights currentLaddermen currentMacemen currentPikemen currentPopulation currentPopulation_2
            currentResources[] currentSiegeWeaponCount currentSpearmen currentSwordsmen currentTunnelers defensesDamagedByPlayer
            dogCageCount engineerCountRelated farmsWithoutWorkers fearFactorLevel foodClock foodClockSpeed foodStorageLevel
            foodStorageLevelLastLastMonth foodStorageLevelLastMonth foodTypeToBeEatenNext foodTypesCurrentlyEaten foodTypesInStock
            goldDonation goodStuffCount granaryIsAlmostFilledUp healerCount hovelCountUpToEight idlePeasantsCount
            isArmouryAlmostFilledUp isFoodTypeBanned[] lastMonthsBribeTax lastMonthsGold lastMonthsIncomeTax lordKilledByPlayerID
            marketGold meatCount moatTileCount moatsOwned noLabourerBuildingCount objectsLeftUntilNextLevel pitchDitchTileCount
            playerDeathRelated popularity popularityChangeAleBased popularityChangeBasedOnCrowding popularityChangeBasedOnFair
            popularityChangeBasedOnFood popularityChangeBasedOnReligion popularityChangeBasedOnTax popularityChangeFearFactorBased
            popularityReligionBasedDiv25 populationCap populationGrowthStatisticCounter populationGrowth[] previousArmySize
            previousAvailablePeasants previousBlessedPeoplePercentage previousSiegeWeaponsCount rationsSetting religionVar1
            startResources[] storedPopularityPercent taxBribeMonthlyAccumulator taxIncomeMonthlyAccumulator taxesSetting
            totalFood troopsKilled troopsLost weeksWithoutFood weightedLosses workingInnsCount""")),
        (P_, "selten", [f"{g}.{t}" for g in w("armory barracks campground engineersGuild granary keep marketplace mercenaryPost "
                                              "oilSmelter stockpile tunnelersGuild") for t in w("areaEntry id tileEntry xEntry yEntry")]),
        (P_, "einmal", w("""barracksAssemblyPoints[].x barracksAssemblyPoints[].y barracksParadegroundLocationsTotal
            cathedralAssemblyPointX cathedralAssemblyPointY engineersAssemblyPoints[].x engineersAssemblyPoints[].y
            engineersParadegroundLocationsTotal engineersParadegroundLocations[].x engineersParadegroundLocations[].y
            lordID lordUID mercenaryAssemblyPoints[] mercenaryAssemblyPoints[][] tunnelersGuildAssemblyPointX
            tunnelersGuildAssemblyPointY tunnelersGuildParadegroundLocationsTotal tunnelersGuildParadegroundLocations[].x
            tunnelersGuildParadegroundLocations[].y""")),
        (P_, "entbehrlich", w("""childUID commemorationShrinePlacementCountdown counterTrackingPopGoldPopup currentGoldDelayed
            dairyFarmVariationMod4 hasInitialResourceRecievingStarted ignitionTime keepEnclosementRelatedCountdown
            lastTimeSFXNoPlaceInStockpile nervousBikCountdown partialStoneCounter pitchDitchCounterTo4 playerRelatedFlag
            popularityAtWeekTick100 rallySearchOffset rationsSetting2 rationsSetting3 someUnitID01 someUnitIDSelfRef
            someUnitIDSelfRef_2 stoneGainedFraction tacticalPowersBarLevel textYOffset unkHopFarmVariation unkWheatFarmOrientation
            vclock vclockIncrement woodGainedFraction""")),
        (P_, "ki", w("""attackAssaultDelayRelatedValue attackTicker attackedPlayerID availableBoulderGridTiles
            availableIronGridTiles availableOasisGridTiles availableOilGridTiles availableTreeGridTiles canStartSpending
            currentAttackRaidParameter currentAttackWave defWallPatrolRallyTimeHits defWallPatrolRallyTimeWaitCounter enemies
            enemyIDArray[] freshUnitTribeIDs[] freshUnitTribeUIDs[] harrasingEngineRecruitTimeout harrassingSiegeEnginesIndex
            isEngineerRequired isNotNervousByEnemyTroopValue lastEncounteredTroopUnitID lastEncounteredTroopUnitUID
            lastlastEncounteredEnemyPlayerID noFlourTracker noHopsTracker noIronTracker noWoodTracker outerPatrolRallyDelayTracker
            raidRetargetDelayCounter relativeStrengthOfTeamComparedToEnemy resourceRebuildDelay resourcesToAcquireArray[]
            shortestDistanceTile shortestDistanceX shortestDistanceY snoozedBuildings[] someAiCountdown3 someAiCountdown4
            someAiCountdown5 someAiCountdown6 someCounter2 someTile someTotalDefenseTroopsRelatedCountdown someX someXPosition
            someY someYPosition sumOfTotalEnemyUnitsCount top100TargetableBuildingsTracker top100TargetableBuildings[]
            totalAssassinTroops totalAttackTroops totalAttackingEngineerTroops totalDiggingUnitTroops totalEnemyRangedTroopValue
            totalEnemyTroopValue totalEnemyTroopValueByPlayerID[] totalEnemyUnitsCount totalLaddermenTroops totalMaxDefaultTroops
            totalTeamTroopValue totalTroopValue totalTroopsType0 totalTroopsType6 totalTroopsType7 totalTunnelerTroops
            totalUnit2Troops totalUnitBackupTroops totalUnitEngageTroops totalUnitPatrolTroops totalUnitSiegeDefTroops
            unitPatrolRecommandRelatedDelayValue willBuy""")),
        (P_, "unklar", w("count count_2 counter someCountdown01 someKeepRelatedX2 someKeepRelatedY2 someResourceCounter "
                         "structureRelated1") + [f"unknown6.{t}" for t in w("areaEntry id tileEntry xEntry yEntry")]
         + [f"someCount{n}" for n in w("""02 03 04 10 11 12 13 20 21 22 23 24 25 26 27 28 29 30 31 32 33 40 43 44 45 46 47 48 49 50
             51 52 53 54 55 56 57 58 59 60""")]),
    ],
}

# Von der Sichtschranke nur wegen des Namens gesperrt. Alles hier Nicht-Genannte aus dieser Quelle bleibt "unklar".
NACHGEHOLT = {
    "takt": [E_ + n for n in w("""targetID_OR_targetBuildingID targetedUnitID__OR__engineerMannedSiegeEngineRef
        targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID nextTileUnk killedFlagUnk""")]
    + [M_ + "totalGameTicksUnk"],
    "selten": [E_ + n for n in w("""destinationX_2Unk destinationY_2Unk digTileY__OR__countLifeCycleEngineersSentToManSiegeEngine
        lastEncounteredEnemyUnitIDUnk movementType_OR_targetUnitID assassinsMicroDistanceToEnemyUnk idleCounterUnk
        horseOriginStableIDUnk horseOriginStablesBuildingIndexUnk isSelectable_OR_matchTime""")]
    + [G_ + "idleTimerUnk", M_ + "noRushTicksLeftUnk"]
    + [T_ + n for n in w("percentageAttackingUnk percentageDyingUnk percentageMovingUnk percentageShootingUnk isRallyingUnk size2Unk")]
    + [P_ + n for n in w("""blessedPeopleCountUnk unblessedPeopleCountUnk averagePopulationGrowthUnk populationRelatedCrowdingCountUnk
        priestCountUnk nonInteractiveCitizenCountUnk ownsCathedralUnk ownsChurchUnk fearFactorProductivityUnk
        requestStateUnk requestedAttackTargetUnk requestedGoodsArray1Unk[] requestedGoodsArray2Unk[] playerID_askerUnk""")]
    + w("DAT_CurrentPlayerUnitLosses DAT_UnitValueLossesPerEnemyPlayer DAT_UnitValueLossesPerEnemyPlayer[] "
        "DAT_DestroyedBuildingsCountHistory DAT_DestroyedBuildingsCountHistory[]"),
    "einmal": [E_ + n for n in w("someUnitStat2_meleeDamageUnk enemyNoticeFrequencyUnk moveableUnk")]
    + [G_ + "terrainHeightUnk"] + [Q_ + n for n in w("velocityUnk speedUnk")] + [P_ + n for n in w("ladyIDUnk jesterIDUnk")],
    "entbehrlich": [E_ + n for n in w("""isDisappearingUnk friendlyFireCounterUnk gmIDUnk imageIDUnk spriteHeightUnk spriteWidthUnk
        currentTilePosition_2Unk unitSpeedMatchingRelatedUnk""")]
    + [G_ + n for n in w("playerColorUnk surfaceAreaUnk")] + ["pathLinkageKeepWasUpdatedUnk"]
    + [Q_ + n for n in w("hasDoneEffectUnk colorUnk graphicRotationUnk someCounter_OR_hitGround unitID_OR_seaGullID")]
    + [P_ + n for n in w("childTargetIDUnk rallySearchOffsetsUnk[]")]
    + ["DAT_CounterFoodWarningInterval", "trees[].animationFrameUnk", "trees[].animationFrame2Unk"],
    "ki": [E_ + "engineerRelatedUnk"] + [P_ + n for n in w("""attackedPlayerID_2Unk harassingSiegeEnginesCountUnk highestLoadedQuarryUnk
        monkTribeIDUnk monkTribeUIDUnk noBeerCounterUnk totalDefensiveTroopsUnk totalRaidingTroopsUnk hasMarketUnk""")],
}

# Was der Kern liest (welt.rs, leitung.rs; Kern 21, Aufbau 5, B-169); Versatz -> Name aus OpenSHC Unit.hpp / Building.hpp (Gebaeude: Versatz - 0x14).
NEU_EINHEIT = w("""animationFrame animationCycleNumber targetUID nextTileUnk climbingState terrainOrClimbHeight buildingHeight
    shootTargetMicroX shootTargetMicroY shootTargetZ currentIndexInPathPlan totalSizeOfPathPlan closestEnemyMicroDistance
    plannedDestinationX plannedDestinationY shootTargetedUnit calculatedMovementSpeed destinationNeeded substate killedFlagUnk""")
SONST_NEU = [Q_ + n for n in w("entityType fireIntensity height logicalState microX microY orientation owner tile travelledDistance vCos vSin xPosition yPosition")]
SONST_NEU += [T_ + n for n in w("targetBuildingID targetBuildingUID targetX targetY tribeState")]
SONST_NEU += [P_ + "closestEnemyDistanceToTheLord"]
KERN_EINHEIT = w("""unitType logicalState dying owner microXPosition microYPosition health state targetingType
    targetedUnitID__OR__engineerMannedSiegeEngineRef targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID
    targetID_OR_targetBuildingID target targetX targetY destinationXPosition destinationYPosition ifSelectedThenPlayerID
    selectionRelatedFlag tribeID tribeUID resourceToDeposit workplaceBuildingID_1 attackedUnitID attackedBy targetedBuildingTile
    attackAtTileX attackAtTileY""") + NEU_EINHEIT
KERN_GEBAEUDE = w("""logicalState buildingType owner x y currentHealth uid currentNumberOfResource currentLimitOfResource
    currentStoredResourceType quarryStockpileID widthOrHeight fireDuration gateState""")
KERN_SONST = [P_ + "currentResources[]", "LogicLayer[]", "PathConnectionLayer[]", *SONST_NEU]
# Was davon im gemeinsamen Speicher bei Python ankommt (kern_leitung.EINHEIT_FELDER, GEBAEUDE_FELDER, Vorrat)
PY_EINHEIT = w("""health owner unitType microXPosition microYPosition state destinationXPosition destinationYPosition tribeID targetingType
    targetedUnitID__OR__engineerMannedSiegeEngineRef targetID_OR_targetBuildingID attackedUnitID
    targetedUnitUIDUnk_OR_someAppearTileUnk_OR_buildingUID_OR_pitchDitchUID_OR_entityUID targetedBuildingTile target targetX targetY
    attackedBy attackAtTileX attackAtTileY""") + NEU_EINHEIT
PY_GEBAEUDE = w("buildingType owner x y currentHealth fireDuration gateState")
PY_SONST = [P_ + "currentResources[]", *SONST_NEU]

# Kommt nicht als eigener Wert an, steckt aber in dem, was ankommt: x/y = Feinposition / 8, tile folgt daraus, Tote filtert der Kern
# weg (nur Lebende stehen in der Tabelle), der Taktzaehler steht im Kopf.
STAND_ANKUNFT = "Kern 21, Aufbau 5, B-169; im Spiel bei Tempo 200 geprueft, siehe kern_felder_1108c_200.json"
STECKT_DRIN = {E_ + n for n in w("x y tile destinationTilePosition dying logicalState")} | {G_ + "logicalState", M_ + "totalGameTicksUnk"}


def zuordnung():
    """(Bereich, Feld) -> Bedarf aus der Namensliste."""
    aus = {}
    for bereich, zeilen in GRUPPEN.items():
        for vorsatz, bedarf, namen in zeilen:
            for n in namen:
                k = (bereich, vorsatz + n)
                assert k not in aus, k
                aus[k] = bedarf
    return aus


def zusatz():
    """Feld -> Bedarf fuer die Felder, die die Sichtschranke nur wegen des Namens sperrte."""
    aus = {}
    for bedarf, namen in NACHGEHOLT.items():
        for n in namen:
            assert n not in aus, n
            aus[n] = bedarf
    return aus


BEZUG = [
    (r"^units\[\]", "einheit"),
    (r"^buildings\[\]", "gebaeude"),
    (r"^tribes\[\]", "trupp"),
    (r"^(entityArray|seagullArray)\[\]", "geschoss"),
    (r"^playerDataArray\[\]", "spieler"),
    (r"Layer\[\]$", "kartenfeld"),
    (r"^(moats|pitchDitches|rocks|trees|grid)\[\]", "landschaft"),
]


def bezug(feld):
    for muster, name in BEZUG:
        if re.search(muster, feld):
            return name
    return "allgemein"


def kern_liest(feld):
    if feld in KERN_SONST:
        return "ja"
    if feld.startswith(E_) and feld[len(E_):] in KERN_EINHEIT:
        return "ja"
    if feld.startswith(G_) and feld[len(G_):] in KERN_GEBAEUDE:
        return "ja"
    return "nein"


def python_sieht(feld):
    if feld in PY_SONST:
        return "ja"
    if feld.startswith(E_) and feld[len(E_):] in PY_EINHEIT:
        return "ja"
    if feld.startswith(G_) and feld[len(G_):] in PY_GEBAEUDE:
        return "ja"
    return "nein"


def ankunft(feld, bedarf):
    """Kommt ein Takt-Feld jeden Takt bei Python an? (Stand des Codes, siehe STAND_ANKUNFT)"""
    if python_sieht(feld) == "ja":
        return "direkt"
    if feld in STECKT_DRIN:
        return "steckt_drin"
    return "fehlt" if bedarf == "takt" else ""


def art_name_unklar(feld):
    """Wie die Sichtschranke zu 'unbekannt' kam: reine Platzhalter bleiben aussen vor."""
    blatt = feld.split(".")[-1].replace("[]", "")
    return "_OR_" in blatt or bool(re.search(r"Unk|unknown", blatt))


NUR_ZUSATZ = {n for v in NACHGEHOLT.values() for n in v}

INIT = re.compile(r"^(Launch|loadMap|setup|setUnitValues|create|Upgrade|migrate|Initialize|setStarting|spawn|place|commit|import|SetAI|"
                  r"resetTeams|assignName|determine|SetHovel|SetUndamaged|SetBuildings|clearRocks|clearAll|copyPlayerData|initial|"
                  r"InitMulti|initMulti|changeMapOrient|resetHeight|set[A-Z]\w*Assembly|SetUnitAssembly|setMoatVisual|Version)")
KI = re.compile(r"^(ai[A-Z]|updateAI|planToBuy|selectAttackTarget|recomputeAI|recruitHarrassing|useAITribe|setCurrentAttack|"
                r"recomputeTroopValues|teamIsWeak|computeEnemyKeep|findAttackTribe|getTargetableBuilding|addBuilding|assignAttack|"
                r"decideOnTribe|claimArcher|AssignTribeToSupport|updateTribeLocations|setTargetForTribe|harassBuildings|placeSiegeTent)")


def erwartung(zeile, nie):
    """Zweiter Weg, unabhaengig von der Namensliste oben: nur aus Messung (nie geaendert) und schreibenden Funktionen."""
    if nie:
        return "nie_geaendert"
    n = int(zeile["schreiber"])
    if n == 0:
        return "kein_schreiber"
    namen = zeile["beispiel"].split()
    if n <= len(namen):  # beispiel nennt hoechstens drei; nur dann ist die Liste vollstaendig
        if all(KI.match(x) for x in namen):
            return "nur_ki"
        if all(INIT.match(x) for x in namen):
            return "nur_anlegen"
    return "laeuft"


def main():
    schranke = list(csv.DictReader(open(os.path.join(HIER, "sichtschranke.csv"), encoding="utf-8"), delimiter=";"))
    felder = list(csv.DictReader(open(os.path.join(HIER, "zustand_felder.csv"), encoding="utf-8"), delimiter=";"))
    assert len(schranke) == len(felder) and all(s["bereich"] == f["bereich"] for s, f in zip(schranke, felder, strict=True))
    nie = {(r["global"], r["feld"]) for r in csv.DictReader(
        open(os.path.join(HIER, "lauf_k_20261102", "nie_gesehen_lauf_f_und_k.csv"), encoding="utf-8"), delimiter=";")}

    liste, nach = zuordnung(), zusatz()

    def nutzbar(s):
        return s["eigen"] == "erlaubt" or s["fremd"] in ("erlaubt", "schaetzen")

    ohne = [(s["bereich"], s["feld"]) for s in schranke if nutzbar(s) and (s["bereich"], s["feld"]) not in liste and s["feld"] not in nach]
    assert not ohne, f"{len(ohne)} nicht eingeordnet: {ohne}"
    aus, benutzt, zusatz_benutzt = [], set(), set()
    for s, f in zip(schranke, felder, strict=True):
        name = s["feld"]
        k = (s["bereich"], name)
        if k in liste:
            benutzt.add(k)
            bedarf, quelle = liste[k], "schranke"
        elif name in nach or (s["eigen"] == "unbekannt" and art_name_unklar(name)):
            bedarf, quelle = nach.get(name, "unklar"), "name_unklar"
            zusatz_benutzt.add(name)
        else:
            continue
        gesperrt = bedarf in ("ki", "zufall", "unklar")
        assert nutzbar(s) != gesperrt or bedarf == "entbehrlich", f"Marke passt nicht zum Bedarf: {k} {s['eigen']} {s['fremd']} {bedarf}"
        ng = (f["global"], f["feld"]) in nie
        aus.append({"bereich": s["bereich"], "feld": name, "bezug": bezug(name), "eigen": s["eigen"], "fremd": s["fremd"], "bedarf": bedarf,
                    "quelle": quelle, "kern_liest": kern_liest(name), "python_sieht": python_sieht(name),
                    "nie_geaendert_F_K": "ja" if ng else "nein", "schreiber": f["schreiber"], "beispiel": f["beispiel"],
                    "zweiter_weg": erwartung(f, ng), "ankunft": ankunft(name, bedarf)})
    fehlt = set(liste) - benutzt
    assert not fehlt, f"in der Liste, aber nicht vorhanden: {sorted(fehlt)[:30]}"
    fehlt = set(nach) - zusatz_benutzt
    assert not fehlt, f"nachgeholt, aber nicht vorhanden: {sorted(fehlt)[:30]}"

    with open(os.path.join(HIER, "feldliste_gehirn.csv"), "w", encoding="utf-8", newline="") as d:
        schreiber = csv.DictWriter(d, fieldnames=list(aus[0]), delimiter=";")
        schreiber.writeheader()
        schreiber.writerows(aus)

    print("Zeilen", len(aus), collections.Counter(x["quelle"] for x in aus))
    print("Bedarf", collections.Counter(x["bedarf"] for x in aus).most_common())
    print("nutzbar", sum(x["eigen"] == "erlaubt" or x["fremd"] in ("erlaubt", "schaetzen") for x in aus))
    print("Bedarf x zweiter Weg")
    t = collections.Counter((x["bedarf"], x["zweiter_weg"]) for x in aus)
    wege = sorted({k[1] for k in t})
    print(f"{'':12}" + "".join(f"{v:>15}" for v in wege))
    for b in BEDARFE:
        print(f"{b:12}" + "".join(f"{t[(b, v)]:>15}" for v in wege))
    bericht(aus)


BEDARFE = ("takt", "selten", "einmal", "entbehrlich", "ki", "zufall", "unklar")
BEZUEGE = ("einheit", "gebaeude", "trupp", "geschoss", "spieler", "kartenfeld", "landschaft", "allgemein")


def bericht(aus):
    """Feldliste_Gehirn.md aus denselben Zahlen wie die Liste."""
    def kurz(zeilen):
        return ", ".join(f"`{x['feld'].split('.', 1)[-1] if x['bezug'] != 'allgemein' else x['feld']}`" for x in zeilen)

    zahl = collections.Counter((x["bezug"], x["bedarf"]) for x in aus)
    z = ["# Feldliste fürs Gehirn (B-168)", "",
         "Erzeugt von `feldliste_gehirn.py`, ohne Spielstart. Ganze Liste: `feldliste_gehirn.csv`.", "",
         f"**{len(aus)} Felder**, davon {sum(x['eigen'] == 'erlaubt' or x['fremd'] in ('erlaubt', 'schaetzen') for x in aus)} "
         "fürs Gehirn nutzbar, mindestens für die eigene Seite.", "",
         "| Bezug | " + " | ".join(BEDARFE) + " | zusammen |", "|---|" + "---|" * (len(BEDARFE) + 1)]
    for b in BEZUEGE:
        z.append(f"| {b} | " + " | ".join(str(zahl[(b, k)]) for k in BEDARFE) + f" | {sum(zahl[(b, k)] for k in BEDARFE)} |")
    z.append("| **alle** | " + " | ".join(str(sum(zahl[(b, k)] for b in BEZUEGE)) for k in BEDARFE) + f" | {len(aus)} |")
    z += ["", "- **takt:** jeden Takt nötig. **selten:** bei Änderung oder alle paar Takte. **einmal:** beim Entstehen oder zum Partiestart.",
          "- **entbehrlich:** nur Bild, Hilfswert der Engine oder ableitbar. **ki, zufall:** fürs Gehirn gesperrt. **unklar:** ungenutzt, bis geklärt.",
          "", f"## Was jeden Takt ankommt ({STAND_ANKUNFT})", "",
          "| Bezug | takt-Felder | liest der Kern | kommt bei Python an | steckt drin | fehlt |", "|---|---|---|---|---|---|"]
    fehlend = {}
    for b in BEZUEGE:
        t = [x for x in aus if x["bezug"] == b and x["bedarf"] == "takt"]
        if not t:
            continue
        an = [x for x in t if x["python_sieht"] == "ja"]
        drin = [x for x in t if x["python_sieht"] != "ja" and x["feld"] in STECKT_DRIN]
        fehlend[b] = [x for x in t if x["python_sieht"] != "ja" and x["feld"] not in STECKT_DRIN]
        z.append(f"| {b} | {len(t)} | {sum(x['kern_liest'] == 'ja' for x in t)} | {len(an)} | {len(drin)} | {len(fehlend[b])} |")
    t = [x for x in aus if x["bedarf"] == "takt"]
    z.append(f"| **alle** | {len(t)} | {sum(x['kern_liest'] == 'ja' for x in t)} | {sum(x['python_sieht'] == 'ja' for x in t)} | "
             f"{sum(x['python_sieht'] != 'ja' and x['feld'] in STECKT_DRIN for x in t)} | {sum(len(v) for v in fehlend.values())} |")
    sel = [x for x in aus if x["bedarf"] in ("selten", "einmal")]
    z += ["", f"Von den {len(sel)} Feldern für selten und einmal liest der Kern {sum(x['kern_liest'] == 'ja' for x in sel)}, "
          f"bei Python kommen {sum(x['python_sieht'] == 'ja' for x in sel)} an.", "", "### Fehlende takt-Felder", ""]
    z += [f"- **{b}** ({len(v)}): {kurz(v)}" for b, v in fehlend.items() if v] or ["Keine."]
    z += ["", "Ob ein Feld auch für fremde Einheiten gelesen werden darf, steht in der Spalte `fremd`. Die neuen Felder schwärzt der Kern für Fremde. "
          "Noch ungefiltert an Python gehen die sieben alten Felder Laufziel x und y, Gruppe, Zielart, Zieleinheit, Zielgebäude und Nahziel; "
          "die Sperre dafür kommt mit dem Gehirn (B-152).", "",
          "## Sichtschranke", "",
          "Die Spalten `eigen` und `fremd` kommen aus `sichtschranke.csv`. Was nach dieser Liste dort korrigiert wurde, "
          "steht Feld für Feld in `sichtschranke_zweifel.md`.", ""]
    zw = collections.Counter((x["bedarf"], x["zweiter_weg"]) for x in aus)
    z += ["## Gegenprobe", "",
          "Zweiter Weg, unabhängig von der Namensliste: Messung aus Lauf F und K (nie geändert) und die schreibenden Funktionen.", "",
          f"- takt, aber nie geändert: **{zw[('takt', 'nie_geaendert')]}**. takt, aber nur beim Anlegen geschrieben: **{zw[('takt', 'nur_anlegen')]}**.",
          f"- einmal, aber auch im Lauf geschrieben: {zw[('einmal', 'laeuft')]}, einzeln durchgesehen: Besitzerwechsel beim Tod eines Spielers, Werte je Schuss und Werte beim Bau.",
          f"- selten, aber nur beim Anlegen geschrieben: {zw[('selten', 'nur_anlegen')]}, fast alle Eingänge von Gebäuden: Sie entstehen, wenn gebaut wird.",
          f"- ki, aber auch im Lauf geschrieben: {zw[('ki', 'laeuft')]}. Schreiber ist meist `updateUnits` oder eine andere Sammelfunktion. 17 der Spieler-Felder liest auch Code außerhalb der KI, zum Beispiel `enemies` und `totalEnemyTroopValue`; sie lassen sich aus sichtbaren Einheiten und Teams selbst rechnen.",
          "", "## Grenzen", "",
          "- **Belegt** ist, welche Felder sich in Lauf F und K nie änderten und welche Funktionen schreiben.",
          "- **Einschätzung** ist die Trennung von takt und selten: Wie oft sich jedes Feld ändert, ist nicht gemessen, die Rohaufzeichnungen liegen auf dem anderen PC.",
          "- **Einschätzung** ist auch entbehrlich. Es heißt nicht unsichtbar, sondern nur: nicht jeden Takt liefern.",
          f"- **Offen:** {sum(x['bedarf'] == 'unklar' for x in aus)} unklare Felder hier und die reinen Platzhalter, die gar nicht in dieser Liste stehen.", ""]
    with open(os.path.join(HIER, "Feldliste_Gehirn.md"), "w", encoding="utf-8", newline="\n") as d:
        d.write("\n".join(z))


if __name__ == "__main__":
    main()

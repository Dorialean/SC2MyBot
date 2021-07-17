import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.effect_id import EffectId
import random

class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilator()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def build_assimilator(self):
        for nexus in self.units(UnitTypeId.NEXUS).ready:
            vespens = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vespens in vespens:
                if not self.can_afford(UnitTypeId.ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespens.position)
                if worker is None:
                    break
                if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, vespens).exists:
                    await self.do(worker.build(UnitTypeId.ASSIMILATOR, vespens))
    async def build_workers(self):
        for nexus in self.units(UnitTypeId.NEXUS).ready.idle:
            if self.can_afford(UnitTypeId.PROBE):
                await self.do(nexus.train(UnitTypeId.PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(UnitTypeId.PYLON):
            nexuses = self.units(UnitTypeId.NEXUS).ready
            if nexuses.exists:
                await self.build(UnitTypeId.PYLON, near=nexuses.first)

    async def expand(self):
        if self.units(UnitTypeId.NEXUS).amount < 3 and self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()

    async def offensive_force_buildings(self):
        if self.units(UnitTypeId.PYLON).ready.exists:
            pylon = self.units(UnitTypeId.PYLON).ready.random
            if self.units(UnitTypeId.GATEWAY).ready.exists and not self.units(UnitTypeId.CYBERNETICSCORE).ready.exists:
                if self.can_afford(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(UnitTypeId.CYBERNETICSCORE):
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            elif len(self.units(UnitTypeId.GATEWAY)) < 3:
                if self.can_afford(UnitTypeId.GATEWAY) and not self.already_pending(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def build_offensive_force(self):
        for gateway in self.units(UnitTypeId.GATEWAY).ready.noqueue:
            if self.can_afford(UnitTypeId.STALKER) and self.supply_left > 0:
                await self.do(gateway.train(UnitTypeId.STALKER))


    async def attack(self):
        if self.units(UnitTypeId.STALKER).amount > 15:
            for st in self.units(UnitTypeId.STALKER).idle:
                await self.do(st.attack(self.enemy_start_locations[0]))
        elif self.units(UnitTypeId.STALKER).amount > 4:
            if self.known_enemy_units.amount > 0:
                for st in self.units(UnitTypeId.STALKER).idle:
                    await self.do(st.attack(random.choice(self.known_enemy_units)))


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, SentdeBot()),
    Computer(Race.Terran, Difficulty.Medium)
    ], realtime=False)
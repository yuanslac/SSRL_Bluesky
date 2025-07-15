from ophyd import Device, Component as Cpt, EpicsSignalRO

class BeamlineCounters(Device):
    """
    Beamline analog input device including:

    - I0, I1, I2: from analog input PVs (e.g., ion chambers or diodes)
    - beamstop_pd: photodiode signal embedded in the beamstop

    All signals are read-only.
    """
    i0 = Cpt(EpicsSignalRO, 'RIO1:GalilAi0_MON.VAL', name='I0')
    i1 = Cpt(EpicsSignalRO, 'RIO1:GalilAi1_MON.VAL', name='I1')
    i2 = Cpt(EpicsSignalRO, 'RIO1:GalilAi2_MON.VAL', name='I2')
    beamstop_pd = Cpt(EpicsSignalRO, 'RIO1:GalilAi3_MON.VAL', name='beamstop_pd')

    def __init__(self, prefix='BL17-2:', **kwargs):
        super().__init__(prefix, **kwargs)

        # configure read_attrs 
        self.read_attrs = ['i0', 'i1', 'i2', 'beamstop_pd']
        self.i0.kind = 'hinted'
        self.i1.kind = 'hinted'
        self.i2.kind = 'hinted'
        self.beamstop_pd.kind = 'normal'

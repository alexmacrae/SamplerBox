menu = {
    'submenu': {

        0: {
            'name': 'Setlist',
            'desc': 'Manage the presets in your setlist',
            'submenu': {
                0: {'name': 'Rearrange', 'desc': 'Select a preset to move to a different place in the setlist',
                    'fn': ['SelectSong', 'MoveSong']},
                1: {'name': 'Remove missing', 'fn': 'SetlistRemoveMissing'},
                2: {'name': 'Delete songs', 'fn': ['SelectSong', 'DeleteSong']}
            }
        },
        1: {
            'name': 'Edit definitions',
            'desc': 'Change sample-set definitions',
            'fn': ['SelectSong', 'EditDefinition']
            },
        2: {
            'name': 'Auto chords',
            'desc': 'Toggle the auto chorder: play chords based on a single note',
            'submenu': {
                0: {
                    'name': 'Chord mode',
                    'desc': 'Select a chord mode style',
                    'fn': 'ChordMode'
                },
                1: {
                    'name': 'Key',
                    'desc': 'Change the key/scale that chords are built around',
                    'fn': 'ChordKey'
                }
            }
        },
        3: {
            'name': 'Master volume',
            'desc': 'Modify the system\'s master volume',
            'fn': 'MasterVolumeConfig'
        },
        4: {'name': 'MIDI Mapping',
            'desc': 'Map any MIDI control to various playback and system features',
            'submenu': {
                0: {
                    'name': 'Master volume',
                    'desc': 'Map a fader or pot to affect volume',
                    'function_to_map': 'gv.ac.master_volume.setvolume',
                    'submenu': {
                        0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                        1: {'name': 'Min', 'desc': '', 'params': [-70]},
                        2: {'name': 'Max', 'desc': '', 'params': [0]},
                        3: {'name': 'Delete', 'desc': '', 'fn': 'DeleteMidiMap'}
                    }
                },
                1: {
                    'name': 'Reverb',
                    'desc': 'Map a MIDI control to each of the 5 reverb parameters',
                    'submenu': {
                        0: {
                            'name': 'Room size',
                            'desc': '',
                            'function_to_map': 'gv.ac.reverb.setroomsize',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Damping',
                            'desc': '',
                            'function_to_map': 'gv.ac.reverb.setdamp',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Wet',
                            'desc': '',
                            'function_to_map': 'gv.ac.reverb.setwet',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Dry',
                            'desc': '',
                            'function_to_map': 'gv.ac.reverb.setdry',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        4: {
                            'name': 'Width',
                            'desc': '',
                            'function_to_map': 'gv.ac.reverb.setwidth',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        }
                    }
                },
                2: {
                    'name': 'Voices',
                    'desc': 'For presets that have samples allocated to voices',
                    'submenu': {
                        0: {
                            'name': 'Voice 1',
                            'desc': '',
                            'function_to_map': 'gv.ac.voice.voice1',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Voice 2',
                            'desc': '',
                            'function_to_map': 'gv.ac.voice.voice2',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Voice 3',
                            'desc': '',
                            'function_to_map': 'gv.ac.voice.voice3',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Voice 4',
                            'desc': '',
                            'function_to_map': 'gv.ac.voice.voice4',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                    }
                },
                3: {
                    'name': 'Pitch bend',
                    'desc': 'Map to a control. Perhaps you don\'t have a pitch wheel',
                    'function_to_map': 'gv.ac.pitchbend.set_pitch',
                    'submenu': {
                        0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                4: {
                    'name': 'ModWheel:unavail',
                    'desc': 'Unavailable at this time',
                    'function_to_map': 'gv.ac.mod_wheel.set_modulation_disabled',
                    'submenu': {
                        0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                5: {
                    'name': 'Sustain',
                    'desc': 'Map an unconventional control to the sustain pedal',
                    'function_to_map': 'gv.ac.sustain.set_sustain',
                    'submenu': {
                        0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                6: {
                    'name': 'System Navigation',
                    'desc': 'Map additional system navigation controls',
                    'submenu': {
                        0: {
                            'name': 'Left',
                            'desc': '',
                            'function_to_map': 'gv.nav.state.left',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Right',
                            'desc': '',
                            'function_to_map': 'gv.nav.state.right',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Enter',
                            'desc': '',
                            'function_to_map': 'gv.nav.state.enter',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Cancel',
                            'desc': '',
                            'function_to_map': 'gv.nav.state.cancel',
                            'submenu': {
                                0: {'name': 'Learn', 'desc': '', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        }
                    }
                }
            }
            },
        5: {'name': 'System settings',
            'desc': 'Modify settings and save them to your config.ini',
            'submenu': {
                0: {'name': 'Audio Device', 'desc': 'Select a different audio device', 'fn': 'AudioDevice'},
                1: {'name': 'Max polyphony', 'desc': 'The max number of samples can be played simultaneously', 'fn': 'MaxPolyphonyConfig'},
                2: {'name': 'MIDI channel', 'desc': '', 'fn': 'MidiChannelConfig'},
                3: {'name': 'Audio channels', 'desc': '', 'fn': 'ChannelsConfig'},
                4: {'name': 'Buffer size', 'desc': '', 'fn': 'BufferSizeConfig'},
                5: {'name': 'Sample rate', 'desc': '', 'fn': 'SampleRateConfig'},
                6: {'name': 'Reverb ON/OFF', 'desc': '', 'fn': 'ToggleReverb'}

            }

            },
        # 6: {'name': 'Restart', 'fn': 'gv.sysfunc.restart()'},

    }
}

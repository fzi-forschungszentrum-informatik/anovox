# Instructions - Carla

First, we need to look for assets that we can import into Unreal Engine 4. Only fbx assets can be inserted into Unreal
Engine 4, so it's best to search for .fbx files directly. There are many free assets with CC Attribution available
on [www.sketchfab.com](http://www.sketchfab.com/).

Once you've chosen an asset, download its .fbx file and copy the creator's credit link. You can paste this link into an
Excel file, for example.

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/F09C5E9E-380F-453A-A2F8-ABD8050CB21D_2/lBRzxxDyCevbLHXcTRxIUMsmD5yBDGd7BXssJjdJllQz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/54B0C20F-AD37-466F-B84F-22819A097117_2/vLJ5dYb8cjBr8kmInYfXJejIYckbmccC4CX2eP4IVgoz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/16DF8AD9-B316-41C4-AB5C-8B36AFD51572_2/orBCfK8spw2VnkHnn6zPeVchxFrx3VgiGD2tGFtDLxEz/Image.png)

----

Import the unpacked file into Unreal Engine 4 (Carla version), preferably into the folder that corresponds to the tag of
the object. In this case, import it into the Home folder.

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/AFDAB5D5-7F33-4EF5-8E9D-E47625D40C2F_2/asOn1QAglfPy5qByDIlfO3bASDcL08uBbj7fiYsCgngz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/01CBB8CE-45B6-4B86-98AA-C62A652729F6_2/QCwakYA78YsJtaC7QujFF2LUHLzNWIHebQNQAH2qymsz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/CCCBA1F5-BA20-4602-90A5-DC5A5C6780AB_2/yaJq11iPYOWR3XAnUFziYMYdAyiMbi0Myxr5FleqDiYz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/8CFB34AA-3007-4518-AC37-09568FEB3EF7_2/wWZev6I4FpfzbCOIiDxmkAF3rJ9jCAJgofPyKivX7JUz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/FEDB9579-6D23-416A-8959-282E5E2B08D9_2/tGg472Gbfs03kGHXxyuNoIns6tsTAXLZUdlQ2eZsUv0z/Image.png)

----

When importing some of the materials of the objects may not be automatically created or the material may be colored
white. In such cases, you'll need to manually create a material and add the textures. Some imported files may not even
have textures. For some assets, you can use the materials from other assets.

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/4E310AFF-87D9-49E1-909B-A9BF1C252BF7_2/Cf20WOohNEwYBPwxAS4wXmxZWSxB0MPhACdsVcShpacz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/52DC13AF-4739-4014-8B9D-FD6702805CE7_2/LAkHotMiNh3xzpfJtObLIY3KgMGMZFTeDVUb8sGNhMkz/Image.png)

----

Next, edit the asset. Color it in if it hasn't been done automatically and check if it has a simple collision. If not,
you'll need to add one manually (preferably add 26DOP Simplified Collision), as otherwise the physics and gravity won't
work.

Check if the pivot of the asset is near the object. If not, the object needs to be edited again with Blender.
Unfortunately, there's no way to permanently move the pivot for the blueprint in Unreal Engine 4. You can only change
the pivot point for an instantiated object, so not permanently for a static mesh.

----

In Blender we have to set the 3D Cursor in the World Origin. After that we have to select the Asset and set Origin to 3D
Cursor.

![Screenshot from 2023-03-29 02-07-01.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/D7ADA1D9-27B7-456F-A841-15843CDC8A5E_2/pApNDwrckISyyRSNL30R9ZkqVMVZWyPMmjck5rqHBX0z/Screenshot%20from%202023-03-29%2002-07-01.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/67BDE567-19F3-4146-8804-F19197DE5F5A_2/SBXWr6Us8z5XI2gPfhdqIEcxNcvK9oKcgxz34uSFqLAz/Image.png)

----

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/F7D096EE-6A1D-4357-B78C-6581EC8FA4C7_2/bqyMdt4xTm01oOVZWHaxkt8J4YQG8v2TUKwmLN6dCZ8z/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/026F3DBC-5671-4E82-9730-81650A29B260_2/xI6tjiZdKgBUyaGnxpYAg8JdyJkKF1mW23I2houjZwMz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/07794CFB-1019-4562-9D5D-DA8FE1D1DF1B_2/Na3Nwem1OA0mLpxycGSadZlCZHYSQhyi6FGm3DRnRWgz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/DD23021E-8FD6-4C54-A4F0-2029F785CECF_2/sZ8TSzbWxg5IQ01HJkjkyI4JPBCKXFqyMUyWSuTUWu8z/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/9939375C-ABB1-40A9-9D1F-ED960FD9B7EC_2/a4I99G4aQfxNGEQmJpgxIQeiAZ4ZNikn5STPgFRkjeYz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/49C34CD2-811E-45AF-8FDF-32C662A4D2A1_2/zhMeb6iIVTjE3abz3xxR46oZgJbSKwPnHJI7NJBVRNsz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/E6086079-1917-4F84-9F8A-956A1A02B44C_2/wuVJWsd1Zn2RWapfE4DoEVxGeGG4jqrntu8sNUqHjzIz/Image.png)

----

Finally, we need to add the object to the blueprint. Open the PropFactory file and go to the DefinitionsMap, then add
the object there. Compile and save the blueprint.

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/9ED6BA64-2E4A-41B4-9C98-2E140668268F_2/K1yh3704Kfx2021UvyY7khnSy2Kgda9sTotHjwZgzM4z/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/B3890F6A-BAA3-4F13-9DA1-027C4F702985_2/ty7FE5FxQHvjOmju6gn8nD3PZ7FP6bJmewWcLruib1Uz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/D38F8133-1AB3-4D37-B554-3F12187C00B9_2/XoJ96xByyR7sB1NkU6EUBSKknMQSo6zNd5mJBk3TFzcz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/59AC4030-15A8-4787-9F01-22CB7A0906D0_2/KSd0pA8y3Y9q59kXmdEGtcjd4w2hhNsza61wrQ481q8z/Image.png)

----

Next, we need to add the object to the Default.Package.json file. This is a lot of work if you're adding several
objects, so we've automated this step with a Python program. Save everything, and you're done!

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/CA2FE9E4-4F92-48CA-AEB9-ADB937313373_2/efIHVWeQ8hluvxbJWysleAWMUXc6hIgmL7GTk1ZP1lsz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/B6835744-354A-48EE-B2B4-CDD4F214D79B_2/7ScBxRGhlK5JhNd25k5cWfTPPF00pGygmQqlduNyCp0z/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/54EF2681-AA56-4D8B-B543-C39ED3B56DE4_2/O3emQaZc8rMU9TxopFoCoi6VCVxRuqPqYoxcrQEKwcoz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/9F73372D-05BB-442E-BE17-DD401BC3CE3C_2/7eDiHBZM7h9Yf5KgZJrMzoHQ4vS4ObGoIAwUONmyQh0z/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/F1FCC72B-7596-455E-8246-BBB203323CCC_2/pWh6yBC3KQDwkIJpGJiF8k5x5Q5MStioR7FjdSLTkcwz/Image.png)

----

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/1B362568-52FB-47A9-9490-61C90FDC00E8_2/wLhWKxPtlvW2x2TKzMbPVeVoaO5Rp5Ac7MITtzsIlPcz/Image.png)

----

Additionally, there may be some other problems with the imported objects. Some objects may consist of multiple
individual objects, which all need to be marked, placed in the world, and merged together.

Many objects may also have the wrong size, so you'll need to adjust the size accordingly.

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/4C200A40-604D-4CA0-AB16-AE43F28EAA39_2/GOFPD0wM244AFq9wN8waifc8suudqxl4N53uYirAUegz/Image.tiff)

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/16B17E96-74C9-4953-81D5-7B002B75F2F1_2/yOBEuKdoVT7cdK6hY9gv5xVbJ83tV6O5oT5tsYyy4Vkz/Image.tiff)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/8B947C2E-E457-4499-9B55-5B96BEE32B4E_2/YRIMQqNCtF8yPodZrEXd6fedgyW864yIyIyYeZ1NlCoz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/9DF2AEE7-905A-4048-A4AF-D2F1E99AA997_2/dXfMpZjMfRwpI7TlbOS0xlsPhT9J9vIjtamhpPNH8Yoz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/998A11BD-3891-4FBA-B184-23FF452E57FF_2/uqJi16vudJwUkbEAFxTf4DVWnUbGs9t4i4kWyyMF6SUz/Image.png)

![Image.png](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/872700E7-4E12-47A5-87F1-CA73B0719D86_2/ttxWwc09xAvl6D56A1d6A2zjxtV3Mrruf4u8nVHQ3DMz/Image.png)

----

If you have special objects for which there is no tag in Carla yet, you can follow the steps outlined in the Carla
documentation.

[Create semantic tags - CARLA Simulator](https://carla.readthedocs.io/en/latest/tuto_D_create_semantic_tags/)

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/CA9ADF46-582F-4919-99AA-22BB37017CEB_2/hyZ7ya33AP03m6YI4md1cEIEyAsMmu2036IuKsNy9vkz/Image.tiff)

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/906224ED-63EE-4D6B-9C9D-CEABB8FC3A8B_2/yZVUO3aIFWl4bIhhhD9MuYvJz6pZDOeED5FMADolS3Mz/Image.tiff)

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/5321BBF7-BAD9-4602-BD45-2555CED31D9C_2/6xWoxCBz2GaB6frVtRqdvPBo8vVHVpPYTsWchNNOQ7Qz/Image.tiff)

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/0543B4E2-D95E-4CDD-A897-F8BC1B0F8307_2/kBARKAdujpPNkVwFIBu8xWqxy3ylWAPsDkwRKxySgaUz/Image.tiff)

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/66F6D05A-B79D-4855-9E67-BECC3CE5CF3B_2/XZHvYDVknytUnXvtyVbuOv93o2xIWG32tpvsYT4leywz/Image.tiff)

![Image.tiff](https://res.craft.do/user/full/9a407c9f-6b74-f4d9-8590-e35fd4ff83ec/doc/E7689C60-604A-440A-AC02-B94FC7904BB4/9E59EAA7-7423-430B-B369-AF2F38CACE26_2/ylri5cPphO6OEDSxuQmmnrfRG1txxfAyFfDUoCnsy4Ez/Image.tiff)

----


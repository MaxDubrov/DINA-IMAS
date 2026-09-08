import os, argparse
import math
import imas




def ReadElementData(f):
    output = {}
    
    output["name"] = f.readline().strip()
    
    s = f.readline().strip().split()
    props = [int(p) for p in s]
    if len(props) != 4:
        print("Incorrect properties size: " + str(len(props)))
    output["props"] = props
    
    s = f.readline().strip().split()
    geometry = [float(p) for p in s]
    if len(geometry) != 6:
        print("Incorrect geometry items size: " + str(len(geometry)))     
    output["geometry"] = geometry

    return output


def FillIDSElement(elem, d):
    elem.name = d['name']
    elem.turns_with_sign = float(d['props'][2])

    geometry = d['geometry']
    r = geometry[0]
    z = geometry[1]
    dr = geometry[2]
    dz = geometry[3]
    beta = geometry[4] - math.pi/2.
    alpha = geometry[5]

    tol = 1.e-8
    if abs(alpha) < tol and abs(beta) < tol:
        elem.geometry.geometry_type = 2
        elem.geometry.rectangle.r = r
        elem.geometry.rectangle.z = z
        elem.geometry.rectangle.width = dr
        elem.geometry.rectangle.height = dz
    else:
        elem.geometry.geometry_type = 3
        elem.geometry.oblique.r = r - 0.5*(dr*math.cos(alpha) + dz*math.sin(beta))
        elem.geometry.oblique.z = z - 0.5*(dr*math.sin(alpha) + dz*math.cos(beta))
        elem.geometry.oblique.length_alpha = dr
        elem.geometry.oblique.length_beta = dz
        elem.geometry.oblique.alpha = alpha
        elem.geometry.oblique.beta = beta



def ReadTokamakConfig(filename):

    pf_active = imas.pf_active()
    pf_passive = imas.pf_passive()
    wall = imas.wall()
    magnetics = imas.magnetics()

    pf_active.ids_properties.homogeneous_time = 0
    pf_passive.ids_properties.homogeneous_time = 0
    wall.ids_properties.homogeneous_time = 0
    magnetics.ids_properties.homogeneous_time = 0
    
    f = open(filename, 'rt')

    # Coils
    data = []
    f.readline()
    nae = int(f.readline())
    
    print("nae = " + str(nae))
    for i in range(nae):
        data.append(ReadElementData(f))
    
    npfa = 0
    for d in data:
        npfa = max(npfa, d['props'][3])

    pf_active.coil.resize(npfa)
    for d in data:
        icoil = d['props'][3]-1
        elem = pf_active.coil[icoil].element.getAoSElement()
        pf_active.coil[icoil].element.append(elem)
        FillIDSElement(elem, d)

    
    # Coil resistances
    data = []
    f.readline()
    nres = int(f.readline())
    if nres != npfa:
        print("Incorrect amount of coil resistances: nr=" + str(nres) + ", npfa="+ str(npfa))
    for i in range(nres):
        line = f.readline().rstrip()
        description = line.split()
        pf_active.coil[i].resistance = float(description[0])
    

    # Vessel
    data = []
    f.readline()
    nae = int(f.readline())
    
    print("nae = " + str(nae))
    for i in range(nae):
        data.append(ReadElementData(f))
    
    npfa = 0
    for d in data:
        npfa = max(npfa, d['props'][3])

    pf_passive.loop.resize(npfa)
    for d in data:
        icoil = d['props'][3]-1
        elem = pf_passive.loop[icoil].element.getAoSElement()
        pf_passive.loop[icoil].element.append(elem)
        FillIDSElement(elem, d)

    
    # Vessel resistances
    data = []
    f.readline()
    nres = int(f.readline())
    if nres != npfa:
        print("Incorrect amount of coil resistances: nr=" + str(nres) + ", npfa="+ str(npfa))
    for i in range(nres):
        line = f.readline().rstrip()
        description = line.split()
        pf_passive.loop[i].resistance = float(description[0])
    


    # Loops
    f.readline()
    nloop = int(f.readline())
    print("nloop = " + str(nloop))
    for i in range(nloop):
        line = f.readline().strip().split()
        loop = magnetics.flux_loop.getAoSElement()
        magnetics.flux_loop.append(loop)
        loop.position.resize(1)
        loop.position[0].r = float(line[0])
        loop.position[0].z = float(line[1])
    
    
    # Probes
    f.readline()
    line = f.readline().strip().split()
    nprob = int(line[0])
    print("nprob = " + str(nprob))
    for i in range(nprob):
        line = f.readline().strip().split()
        probe = magnetics.b_field_pol_probe.getAoSElement()
        magnetics.b_field_pol_probe.append(probe)
        probe.position.r = float(line[0])
        probe.position.z = float(line[1])
        probe.poloidal_angle = float(line[2])
        probe.length = float(line[3])
    
    
    # Limiter
    f.readline()
    nlim = int(f.readline())
    print("nlim = " + str(nlim))
    wall.description_2d.resize(1)
    wall.description_2d[0].limiter.unit.resize(1)
    outline = wall.description_2d[0].limiter.unit[0].outline
    outline.r.resize(nlim)
    outline.z.resize(nlim)
    for i in range(nlim):
        line = f.readline().strip().split()
        outline.r[i] = float(line[0])
        outline.r[i] = float(line[1])
    

    f.close()


    # Area
    # f.readline()
    # line = f.readline().strip().split()
    # rmin = float(line[0])
    # rmax = float(line[1])
    # line = f.readline().strip().split()
    # zmin = float(line[0])
    # zmax = float(line[1])
    
    
    return pf_active, pf_passive, wall, magnetics



def SaveTokamakConfig(pf_active, pf_passive, wall, magnetics, f):
    
    # Coils
    recsave = record["coils"]
    f.write("COILS   number:   npf   !tokamak_config.dat  \n") # comment
    f.write(recsave["common_geom"][0].text() + "\n") # npf
    for coil in recsave["geometry"]:
        self.SaveFilePart(f, coil)
    f.write("res_PF:   npf  \n") # comment
    f.write(str(recsave["common_res"][0]) + "\n") # npf
    self.SaveFilePart(f, recsave["resist"])
    
    
    # Vessel
    recsave = record["vessel"]
    f.write("Vessel   number:   ncam  \n") # comment
    f.write(str(recsave["common_geom"][0]) + "\n") # ncam
    for coil in recsave["geometry"]:       
        self.SaveFilePart(f, coil)     
    f.write("res_ves:   ncam  \n") # comment
    f.write(str(recsave["common_res"][0]) + "\n") # ncam
    self.SaveFilePart(f, recsave["resist"])
    
    
    # Loops
    recsave = record["loops"]
    f.write("Loops   number:   kloop  \n") # comment
    f.write(str(recsave["common"][0]) + "\n") # nloop
    nloop = len(recsave["items"])
    for i in range(nloop):
        s1 = recsave["items"][i]["r"].text()
        s2 = recsave["items"][i]["z"].text()
        f.write("  " + s1 + "  " + s2 + "\n")
    
    
    # Probes
    recsave = record["probes"]
    f.write("Probes   number   and   division:   kprobe   kpb \n") # comment
    f.write(recsave["common"][0].text() + "  " + recsave["common"][1].text() + "\n") # nprobes, subdivisions
    #self.SaveFilePart(f, recsave["common"])
    nprobes = len(recsave["items"])
    for i in range(nprobes):
        s1 = recsave["items"][i]["r"].text()
        s2 = recsave["items"][i]["z"].text()
        s3 = recsave["items"][i]["a"].text()
        s4 = recsave["items"][i]["l"].text()
        f.write("  " + s1 + "  " + s2 + "  " + s3 + "  " + s4 + "\n")


    # Limiter
    recsave = record["limiter"]
    f.write("Limiter   number:   n_limiter  \n") # comment
    f.write(str(recsave["common"][0]) + "\n") # nlim
    nlim = len(recsave["items_r"])
    for i in range(nlim):
        s1 = recsave["items_r"][i].text()
        s2 = recsave["items_z"][i].text()
        f.write("  " + s1 + "  " + s2 + "\n")
    
    
    # Area
    recsave = record["area"]
    f.write(recsave["name"] + "\n")
    s1 = recsave["items_r"][0].text()
    s2 = recsave["items_r"][1].text()
    f.write("  " + s1 + "  " + s2 + "\n")
    s1 = recsave["items_z"][0].text()
    s2 = recsave["items_z"][1].text()
    f.write("  " + s1 + "  " + s2 + "\n") 




def main():
  # MANAGEMENT OF INPUT ARGUMENTS
  # ------------------------------
  parser = argparse.ArgumentParser(description=\
          '---- Converts machine data in DINA format, tokamak_config.dat file, to IDS')
  parser.add_argument('-f','--file',help='Name of a file with machine configuration', required=True)
  parser.add_argument('-u','--uri',help='URI of IMAS database to put output IDS',required=True)
  
  args = vars(parser.parse_args())
  
  file = args["file"]
  uri  = args["uri"]
  
  

  pf_active, pf_passive, wall, magnetics = ReadTokamakConfig(file)

  # Store the results
  print("Put IDS's...")
  imas_obj1 = imas.DBEntry(uri, 'w')
  imas_obj1.create()
  
  imas_obj1.put(pf_active)
  imas_obj1.put(pf_passive)
  imas_obj1.put(magnetics)
  imas_obj1.put(wall)

  imas_obj1.close()



if __name__ == '__main__':  # If direct run, not import
  main()

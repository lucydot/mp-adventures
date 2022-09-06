import pickle
import numpy as np
from mp_api import MPRester

#### Notes on dead-end routes attempted
# mpr.phonon.available_fields
# >>> ph_bs, ph_dos, material_id, last_updated 
# mpr.phonon.get_data_by_id("mp-149").ph_bs
# >>> ph_bs is pymatgen.phonon.bandstructure.PhononBandStructureSymmLine object 
# mpr.phonon.get_data_by_id("mp-149").ph_dos
# >>> ph_dos is pymatgen.phonon.dos.CompletePhononDos object
# mpr.phonon.search(elements=["Mg", "Mn", "O"])
# >>> The PhononRester.search method does not exist as no search endpoint is present
# mpr.summary.get_data_by_id("mp-149").has_props
# >>> No phonon properties present
####

tolerance = 1e-5

count=0
phonon_data_count = 0
imaginary_count = 0

imaginary_high_sym = []

f = open("search_log.txt", "w+")

with MPRester("") as mpr:

    experimental_materials = mpr.summary.search(
        theoretical=False, # filter for those marked as experimental on ICSD
        deprecated=False,
        fields=["material_id"]
        )
    
    for material in experimental_materials:

        count+=1
        print(str(count)+"/"+str(len(experimental_materials)))

        try:
            bs = mpr.phonon.get_data_by_id(material.material_id).ph_bs
        except:
            # any entry without phonon data will return an error 
            pass
        else:
            phonon_data_count += 1

            if bs.has_imaginary_freq(tol=tolerance):
                imaginary_count += 1
                bs_branches = bs.branches

                for branch in bs_branches:

                    if (np.any(bs.bands[:,branch['start_index']] < -tolerance) 
                        or np.any(bs.bands[:,branch['end_index']] < -tolerance)):

                        imaginary_high_sym.append(material.material_id)
                        f.write(str(count)+str(material.material_id))
                        break

f.close()

results = {
    "Num_experimental": count,
    "Num_phonon_data": phonon_data_count,
    "Num_imag_freq": imaginary_count,
    "Num_imag_freq_HSP": len(imaginary_high_sym),
    "MP-IDs_imag_freq__HSP": imaginary_high_sym
}
with open('results.pickle', 'wb') as handle:
    pickle.dump(results, handle)




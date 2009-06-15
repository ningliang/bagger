require File.dirname(__FILE__) + "/../db.rb"

# Convenience counts


# Function for processing a single file
def process(file) 
  File.open(file, "r") do |fh|
    # Create the new product
    product = Product.create
    while (line = fh.gets)
      # Parse object type, fields
      object_name, field_string = line.split(":")
      fields = {}
      field_string.split(",").each do |kv_pair|
        key, value = kv_pair.split("=")
        fields[key] = value
      end
      
      # Names, details, tags, photos, purchase points      
      if fields.has_key?("name") and fields.keys.size == 1 and object_name == "tag"
        product.name = fields["name"]        
      elsif fields.has_key?("details") and object_name == "tag"
        product.details = fields["details"]
      elsif object_name == "tag"
        unless product.tags.first(:name => fields["name"])
          # Need a special conversion here since we lump the rest into "meta"
          tag = Tag.create    
          tag.name = fields.delete("name")
          tag.type = fields.delete("type")
          tag.meta = fields
          product.tags << tag 
        end          
      elsif object_name == "photo"
        unless product.photos.first(:url => fields["url"])
          product.photos << Photo.create(fields)  
        end
      elsif object_name == "purchase_point"
        unless product.purchase_points.first(fields)
          product.purchase_points << PurchasePoint.create(fields)
        end
      else
        puts "Unknown: #{object_name} #{fields.to_json}"
      end
    end
    if Product.first(:name => product.name)
      product.destroy
    else
      puts "Saving product with name #{product.name}"
      product.save
    end
  end  
end


# Begin Main Program

# Validate arguments
unless ARGV.length > 0 and File.exists?(ARGV[0])
  puts "Invalid directory"
  exit 1
end
  
# Grab all files from the specified directory and process them
dir = ARGV[0]
Dir.entries(ARGV[0]).each do |file| 
  process("#{dir}/#{file}") unless ["..", ".", ".DS_Store"].include?(file)
end
  
